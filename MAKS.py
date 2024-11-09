import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Load keywords from each .txt file in the database folder
def load_keywords(folder):
    keyword_dict = {}
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            category = filename.replace(".txt", "")
            with open(os.path.join(folder, filename), "r") as file:
                keywords = file.read().splitlines()
                keyword_dict[category] = [kw.strip() for kw in keywords if kw.strip()]
    return keyword_dict

# Search for keywords in a text file
def search_keywords_in_text(text, keyword_dict):
    matches = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for category, keywords in keyword_dict.items():
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', line):  # Whole word matching
                    if category not in matches:
                        matches[category] = []
                    if keyword not in [match[0] for match in matches[category]]:  # Avoid duplicates
                        matches[category].append((keyword, i + 1))
    return matches

# Process input files and write matches to the output file
def process_files(input_files, keyword_dict, output_path, output_format):
    grouped_matches = {}

    for file_path in input_files:
        with open(file_path, "r") as file:
            text = file.read()
            matches = search_keywords_in_text(text, keyword_dict)

            # Group matches by category across files
            for category, keywords in matches.items():
                if category not in grouped_matches:
                    grouped_matches[category] = []
                for keyword, line_number in keywords:
                    grouped_matches[category].append((keyword, os.path.basename(file_path), line_number))

    # Write output based on format
    if output_format == "TXT":
        with open(output_path, "w") as txtfile:
            for category, items in grouped_matches.items():
                txtfile.write(f"Category: {category}\n")
                for keyword, file, line in items:
                    txtfile.write(f"    {keyword} found in {file} on line {line}\n")
                txtfile.write("\n")
    else:  # CSV
        import csv
        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Category", "Matched Keyword", "Input File", "Line Number"])
            for category, items in grouped_matches.items():
                for keyword, file, line in items:
                    writer.writerow([category, keyword, file, line])

# GUI Setup
def main():
    def select_input_files():
        files = filedialog.askopenfilenames(title="Select Input Files", filetypes=[("Text and CSV Files", "*.txt *.csv")])
        if files:
            input_files.extend(files)
            input_files_list.delete(0, tk.END)
            input_files_list.insert(tk.END, *input_files)

    def select_database_folder():
        folder = filedialog.askdirectory(title="Select Database Folder")
        if folder:
            database_folder.set(folder)

    def select_output_location():
        output_format = output_format_var.get()
        ext = ".csv" if output_format == "CSV" else ".txt"
        path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(output_format + " Files", "*" + ext)], initialfile="Result of MalApi")
        if path:
            output_file_path.set(path)

    def run_search():
        if not input_files:
            messagebox.showerror("Error", "Please select input files.")
            return
        if not database_folder.get():
            messagebox.showerror("Error", "Please select the database folder.")
            return
        if not output_file_path.get():
            messagebox.showerror("Error", "Please choose where to save the output file.")
            return

        keyword_dict = load_keywords(database_folder.get())
        process_files(input_files, keyword_dict, output_file_path.get(), output_format_var.get())
        messagebox.showinfo("Success", f"Search completed! Results saved to {output_file_path.get()}")

    # Initialize GUI window
    root = tk.Tk()
    root.title("Malicious API Keyword Search")
    root.geometry("500x400")

    # Input file selection
    input_files = []
    tk.Label(root, text="Input Files:").pack()
    input_files_list = tk.Listbox(root, width=60, height=5)
    input_files_list.pack()
    tk.Button(root, text="Select Input Files", command=select_input_files).pack()

    # Database folder selection
    database_folder = tk.StringVar()
    tk.Label(root, text="Database Folder:").pack()
    tk.Entry(root, textvariable=database_folder, width=50).pack()
    tk.Button(root, text="Select Database Folder", command=select_database_folder).pack()

    # Output format selection
    output_format_var = tk.StringVar(value="CSV")
    tk.Label(root, text="Output Format:").pack()
    tk.Radiobutton(root, text="CSV", variable=output_format_var, value="CSV").pack()
    tk.Radiobutton(root, text="TXT", variable=output_format_var, value="TXT").pack()

    # Output file selection with default name
    output_file_path = tk.StringVar()
    tk.Label(root, text="Output File Location:").pack()
    tk.Entry(root, textvariable=output_file_path, width=50).pack()
    tk.Button(root, text="Choose Save Location", command=select_output_location).pack()

    # Run search button
    tk.Button(root, text="RunSearch", command=run_search).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
