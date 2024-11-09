![](https://github.com/user-attachments/assets/6724e4e9-f69c-4f27-a8f7-96a385cd9386)<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
</head>
<body>

<h1>🛡️ Malicious API Keyword Search Tool</h1>
<p>A Python tool with a user-friendly GUI for cybersecurity professionals to scan <code>.txt</code> and <code>.csv</code> files for malicious API keywords, based on a customizable database of categorized keywords.</p>

<hr>

<h2>🚀 Features</h2>
<ul>
    <li><strong>File Input:</strong> Accepts multiple <code>.txt</code> and <code>.csv</code> files.</li>
    <li><strong>Customizable Database:</strong> Organize malicious keywords into <code>.txt</code> files, each named by category (e.g., <code>Anti-Debugging</code>, <code>Evasion</code>).</li>
    <li><strong>Organized Output:</strong> Results saved as <code>.csv</code> or <code>.txt</code>, grouped by category with details on each match (keyword, file, line number).</li>
    <li><strong>Intuitive GUI:</strong> Easy file selection, output format options, and scan initiation with a simple interface.</li>
</ul>

<hr>

<h2>📦 Database Files</h2>
<p>This repository includes a <code>malicious_api_database.zip</code> file containing <code>.txt</code> files with categorized malicious API keywords. These files serve as a reference and allow you to scan your input files for known malicious calls quickly. You can also add, edit, or create new <code>.txt</code> files to customize the database according to specific requirements.</p>

<p><strong>Why use <code>.txt</code> files for the database?</strong> Text files are lightweight, human-readable, and easy to edit, allowing flexibility for adding or updating keywords without any specific software dependencies. By organizing keywords into separate <code>.txt</code> files by category, users can target specific types of malicious activity during scans.</p>

<p>The initial database of API calls was generated using <a href="https://malapi.io" target="_blank">malAPI.io</a>, an extensive resource for identifying and categorizing potentially malicious API calls.</p>

<hr>

<h2>📝 How It Works</h2>
<ol>
    <li><strong>Select Files:</strong> Choose the files you want to scan.</li>
    <li><strong>Choose Database Folder:</strong> Point to your categorized keywords folder.</li>
    <li><strong>Configure Output:</strong> Set output format (CSV/TXT) and save location.</li>
    <li><strong>Run the Scan:</strong> Click <code>RunSearch</code> to generate results.</li>
</ol>

<hr>

<h2>📄 Example Output</h2>
<p><strong>TXT Format:</strong></p>
<pre>
Category: Anti-Debugging
   CheckRemoteDebuggerPresent found in log.txt on line 120
</pre>

<p><strong>CSV Format:</strong></p>
<table>
    <tr>
        <th>Category</th>
        <th>Keyword</th>
        <th>Input File</th>
        <th>Line</th>
    </tr>
    <tr>
        <td>Anti-Debugging</td>
        <td>CheckRemoteDebuggerPresent</td>
        <td>log.txt</td>
        <td>120</td>
    </tr>
</table>

<hr>

</body>
</html>(https://github.com/user-attachments/assets/93aea727-dd08-48dc-8555-5c3cab09c42a)
