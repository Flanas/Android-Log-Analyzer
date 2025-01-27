import json
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from datetime import datetime
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for both development and PyInstaller bundled mode """
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    else:
        base_path = os.path.abspath(".")  # Current working directory during development
    return os.path.join(base_path, relative_path)

def browse_file():
    Tk().withdraw()  # Hide the main tkinter window
    file_path = askopenfilename(
        title="Select a log file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return file_path

def prompt_save_file():
    Tk().withdraw()  # Hide the main tkinter window
    current_date = datetime.now().strftime("%Y-%m-%d")
    default_name = f"exceptionAnalysis_{current_date}.txt"
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
    crashed_occurrences = []

    for error_type in error_data:
        results[error_type] = {"count": 0, "lines": []}
        unique_lines_per_error[error_type] = {}

    with open(log_file, 'r', encoding='utf-8') as log_file:
        for line_num, line in enumerate(log_file, start=1):
            line_lower = line.lower()

            for error_type, details in error_data.items():
                if error_type == "Crashed":
                    if "crashed" in line_lower:
                        results[error_type]["count"] += 1
                        results[error_type]["lines"].append(line_num)
                        crashed_occurrences.append((line_num, line.strip()))

                else:
                    for keyword in details["keywords"]:
                        if keyword.lower() in line_lower:
                            results[error_type]["count"] += 1
                            if line_num not in results[error_type]["lines"]:
                                results[error_type]["lines"].append(line_num)
                            if keyword not in unique_lines_per_error[error_type]:
                                unique_lines_per_error[error_type][keyword] = line.strip()

    return results, unique_lines_per_error, crashed_occurrences

def main(file_path=None, save_path=None):
    json_file_path = resource_path('keywords.json')  # Locate the JSON file
    try:
        with open(json_file_path, 'r') as f:
            error_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the file 'keywords.json' at {json_file_path}.")
        return

    # Use the provided file_path or prompt the user if it is not provided
    if file_path is None:
        file_path = browse_file()
    if not file_path:
        print("No file selected. Exiting...")
        return

    # Use the provided save_path or prompt the user if it is not provided
    if save_path is None:
        save_path = prompt_save_file()
    if not save_path:
        print("No save location selected. Exiting...")
        return

    with open(save_path, 'w') as output_file:
        def write_and_print(line):
            print(line)
            output_file.write(line + '\n')

        write_and_print(f"Consolidated Error Analysis Report\n")
        write_and_print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        write_and_print(f"File: {file_path}\n")
        write_and_print("=" * 50 + "\n")

        found_errors_line, unique_lines_per_error, crashed_occurrences = search_errors(file_path, error_data)

        for error_type, data in found_errors_line.items():
            write_and_print(f"\n{error_type}:")
            write_and_print(f"  Total Occurrences: {data['count']}")
            if data['lines']:
                write_and_print(f"  Found on Lines: {', '.join(map(str, data['lines']))}\n")
                if error_type == "Crashed":
                    write_and_print("  Errors Found:")
                    for line_num, line_content in crashed_occurrences:
                        write_and_print(f"    Line {line_num}: {line_content}")
                else:
                    write_and_print("  Known Errors:")
                    for keyword, line_content in unique_lines_per_error[error_type].items():
                        write_and_print(f"    - {keyword}: {line_content}")
            else:
                write_and_print("  No occurrences found.\n")

        write_and_print("=" * 50 + "\n")

    print(f"\nAnalysis complete. Consolidated report saved to {save_path}")

if __name__ == "__main__":
    main()
