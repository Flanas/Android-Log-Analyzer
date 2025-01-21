import json
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory, asksaveasfilename
from datetime import datetime
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for both development and PyInstaller bundled mode """
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    else:
        base_path = os.path.abspath(".")  # Current working directory during development
    return os.path.join(base_path, relative_path)

def browse_folder():
    Tk().withdraw()  # Hide the main tkinter window
    folder_path = askdirectory(title="Select a folder containing log files")
    return folder_path

def prompt_save_file(folder_name):
    Tk().withdraw()  # Hide the main tkinter window
    current_date = datetime.now().strftime("%Y-%m-%d")
    default_name = f"{folder_name}_exceptionAnalysis_{current_date}.txt"
    file_path = asksaveasfilename(
        title="Save Analysis Report As",
        initialfile=default_name,
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return file_path

def search_errors(log_file, error_data):
    results = {}
    unique_lines_per_error = {}
    new_errors = {error_type: [] for error_type in error_data if error_type != "Parse"}

    for error_type in error_data:
        results[error_type] = {"count": 0, "lines": []}
        unique_lines_per_error[error_type] = {}

    all_keywords = {
        error_type: [kw for kw in details["keywords"]]
        for error_type, details in error_data.items()
    }

    with open(log_file, 'r', encoding='utf-8') as log_file:
        for line_num, line in enumerate(log_file, start=1):
            line_lower = line.lower()

            for error_type, details in error_data.items():
                matched_keywords = []
                for keyword in details["keywords"]:
                    if (error_type == "Parse" and keyword in line) or \
                       (error_type != "Parse" and keyword.lower() in line_lower):
                        matched_keywords.append(keyword)
                        if line_num not in results[error_type]["lines"]:
                            results[error_type]["lines"].append(line_num)
                        if keyword not in unique_lines_per_error[error_type]:
                            unique_lines_per_error[error_type][keyword] = line.strip()

                if error_type == "Parse" and "PARSE" in line:
                    if line_num not in results[error_type]["lines"]:
                        results[error_type]["lines"].append(line_num)
                        unique_lines_per_error[error_type][f"PARSE (general)"] = line.strip()

                elif error_type != "Parse" and error_type.lower() in line_lower:
                    known_matches = any(kw.lower() in line_lower for kw in all_keywords[error_type])
                    if not known_matches:
                        new_errors[error_type].append(f"Line {line_num}: {line.strip()}")

                if matched_keywords or (error_type == "Parse" and "PARSE" in line):
                    results[error_type]["count"] += 1

    return results, unique_lines_per_error, new_errors

def main():
    json_file_path = resource_path('keywords.json')  # Locate the JSON file
    try:
        with open(json_file_path, 'r') as f:
            error_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the file 'keywords.json' at {json_file_path}.")
        return

    folder_path = browse_folder()
    if not folder_path:
        print("No folder selected. Exiting...")
        return

    folder_name = os.path.basename(folder_path)
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    if not txt_files:
        print("No .txt files found in the selected folder. Exiting...")
        return

    output_file_path = prompt_save_file(folder_name)
    if not output_file_path:
        print("No save location selected. Exiting...")
        return

    with open(output_file_path, 'w') as output_file:
        def write_and_print(line):
            print(line)
            output_file.write(line + '\n')

        write_and_print(f"Consolidated Error Analysis Report\n")
        write_and_print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        write_and_print(f"Folder: {folder_path}\n")
        write_and_print("=" * 50 + "\n")

        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)
            write_and_print(f"Analyzing File: {file_name}\n")
            write_and_print("=" * 25)

            found_errors_line, unique_lines_per_error, new_errors = search_errors(file_path, error_data)

            for error_type, data in found_errors_line.items():
                write_and_print(f"{error_type}:")
                write_and_print(f"  Total Occurrences: {data['count']}")
                if data['lines']:
                    write_and_print(f"  Found on Lines: {', '.join(map(str, data['lines']))}\n")
                    write_and_print("  Known Errors:")
                    for keyword, line_content in unique_lines_per_error[error_type].items():
                        write_and_print(f"    - {keyword}: {line_content}")
                else:
                    write_and_print("  No occurrences found.\n")

                if error_type != "Parse" and error_type in new_errors and new_errors[error_type]:
                    write_and_print(f"\n  New Errors Found: {len(new_errors[error_type])}")
                    for error in new_errors[error_type]:
                        write_and_print(f"    {error}")

                write_and_print("")

            write_and_print("=" * 500 + "\n")

    print(f"\nAnalysis complete. Consolidated report saved to {output_file_path}")

if __name__ == "__main__":
    main()
