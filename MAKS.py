"""
MAKS - Malware API Keyword Search

Scans text output (e.g. `strings`, FLOSS, or import-table dumps of a sample) for
Windows API names commonly abused by malware, grouped by category
(Injection, Evasion, Anti-Debugging, ...).

GUI:  python MAKS.py
CLI:  python MAKS.py sample_strings.txt other.csv -o results.csv
"""
import argparse
import csv
import os
import re
import sys

DEFAULT_DB_NAME = "Malicious API database"


def app_dir():
    """Folder of the script, or of the .exe when built with PyInstaller."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def default_database():
    path = os.path.join(app_dir(), DEFAULT_DB_NAME)
    return path if os.path.isdir(path) else ""


def load_keywords(folder):
    """Each .txt file in the folder is one category; one API name per line."""
    patterns = {}
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".txt"):
            continue
        category = os.path.splitext(filename)[0]
        with open(os.path.join(folder, filename), "r", encoding="utf-8", errors="ignore") as f:
            keywords = sorted({line.strip() for line in f if line.strip()})
        if keywords:
            # One compiled regex per category instead of one search per keyword per line
            alternation = "|".join(re.escape(k) for k in keywords)
            patterns[category] = re.compile(rf"\b({alternation})\b")
    return patterns


def scan_file(path, patterns):
    """Returns {(category, keyword): [first_line, occurrences]} for one file."""
    hits = {}
    # errors="ignore": strings dumps of binaries often contain bytes that are not valid UTF-8
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line_no, line in enumerate(f, start=1):
            for category, regex in patterns.items():
                for match in regex.findall(line):
                    key = (category, match)
                    if key in hits:
                        hits[key][1] += 1
                    else:
                        hits[key] = [line_no, 1]
    return hits


def scan(input_files, patterns):
    """Returns rows: (category, keyword, file, first_line, occurrences)."""
    rows = []
    for path in input_files:
        for (category, keyword), (first_line, count) in scan_file(path, patterns).items():
            rows.append((category, keyword, os.path.basename(path), first_line, count))
    rows.sort(key=lambda r: (r[0], r[2], r[3]))
    return rows


def write_results(rows, output_path, output_format):
    if output_format == "TXT":
        with open(output_path, "w", encoding="utf-8") as out:
            current = None
            for category, keyword, file, line, count in rows:
                if category != current:
                    if current is not None:
                        out.write("\n")
                    out.write(f"Category: {category}\n")
                    current = category
                out.write(f"    {keyword} found in {file} on line {line} ({count}x)\n")
    else:
        with open(output_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.writer(out)
            writer.writerow(["Category", "Matched Keyword", "Input File", "First Line", "Occurrences"])
            writer.writerows(rows)


def summary(rows):
    per_category = {}
    for category, *_ in rows:
        per_category[category] = per_category.get(category, 0) + 1
    return per_category


# ---------------------------------------------------------------- CLI
def run_cli(argv):
    parser = argparse.ArgumentParser(description="Search text dumps for malicious Windows API names.")
    parser.add_argument("inputs", nargs="+", help=".txt/.csv files to scan (e.g. strings output)")
    parser.add_argument("-d", "--database", default=default_database(), help="keyword database folder")
    parser.add_argument("-o", "--output", help="output file (.csv or .txt); prints a table if omitted")
    args = parser.parse_args(argv)

    if not args.database or not os.path.isdir(args.database):
        parser.error(f"database folder not found: {args.database!r}")
    patterns = load_keywords(args.database)
    rows = scan(args.inputs, patterns)

    if args.output:
        fmt = "TXT" if args.output.lower().endswith(".txt") else "CSV"
        write_results(rows, args.output, fmt)
        print(f"{len(rows)} hit(s) written to {args.output}")
    else:
        for category, keyword, file, line, count in rows:
            print(f"{category:<16} {keyword:<32} {file + ':' + str(line):<24} ({count}x)")
    for category, n in summary(rows).items():
        print(f"[{category}] {n} distinct API(s)")
    return 0


# ---------------------------------------------------------------- GUI
def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("MAKS - Malware API Keyword Search")
    root.geometry("540x470")

    input_files = []
    database_folder = tk.StringVar(value=default_database())
    output_format_var = tk.StringVar(value="CSV")
    output_file_path = tk.StringVar()

    def refresh_list():
        files_list.delete(0, tk.END)
        files_list.insert(tk.END, *input_files)

    def select_input_files():
        files = filedialog.askopenfilenames(title="Select Input Files",
                                            filetypes=[("Text and CSV Files", "*.txt *.csv"), ("All files", "*.*")])
        for f in files:
            if f not in input_files:
                input_files.append(f)
        refresh_list()

    def clear_input_files():
        input_files.clear()
        refresh_list()

    def select_database_folder():
        folder = filedialog.askdirectory(title="Select Database Folder")
        if folder:
            database_folder.set(folder)

    def select_output_location():
        ext = ".csv" if output_format_var.get() == "CSV" else ".txt"
        path = filedialog.asksaveasfilename(defaultextension=ext, initialfile="MAKS results",
                                            filetypes=[(output_format_var.get() + " Files", "*" + ext)])
        if path:
            output_file_path.set(path)

    def run_search():
        if not input_files:
            return messagebox.showerror("Error", "Please select input files.")
        if not os.path.isdir(database_folder.get()):
            return messagebox.showerror("Error", "Please select a valid database folder.")
        if not output_file_path.get():
            return messagebox.showerror("Error", "Please choose where to save the output file.")
        try:
            rows = scan(input_files, load_keywords(database_folder.get()))
            write_results(rows, output_file_path.get(), output_format_var.get())
        except OSError as e:
            return messagebox.showerror("Error", f"Could not read or write a file:\n{e}")
        lines = [f"{c}: {n} API(s)" for c, n in summary(rows).items()] or ["No matches found."]
        messagebox.showinfo("Search complete",
                            f"{len(rows)} hit(s) saved to\n{output_file_path.get()}\n\n" + "\n".join(lines))

    tk.Label(root, text="Input Files:").pack(pady=(8, 0))
    files_list = tk.Listbox(root, width=70, height=6)
    files_list.pack()
    buttons = tk.Frame(root)
    buttons.pack()
    tk.Button(buttons, text="Add Files", command=select_input_files).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Clear", command=clear_input_files).pack(side=tk.LEFT, padx=4)

    tk.Label(root, text="Database Folder:").pack(pady=(8, 0))
    tk.Entry(root, textvariable=database_folder, width=62).pack()
    tk.Button(root, text="Select Database Folder", command=select_database_folder).pack()

    tk.Label(root, text="Output Format:").pack(pady=(8, 0))
    fmt = tk.Frame(root)
    fmt.pack()
    tk.Radiobutton(fmt, text="CSV", variable=output_format_var, value="CSV").pack(side=tk.LEFT)
    tk.Radiobutton(fmt, text="TXT", variable=output_format_var, value="TXT").pack(side=tk.LEFT)

    tk.Label(root, text="Output File Location:").pack(pady=(8, 0))
    tk.Entry(root, textvariable=output_file_path, width=62).pack()
    tk.Button(root, text="Choose Save Location", command=select_output_location).pack()

    tk.Button(root, text="Run Search", command=run_search, width=20).pack(pady=12)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(run_cli(sys.argv[1:]))
    run_gui()
