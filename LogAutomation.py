import json
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from datetime import datetime
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for both development and PyInstaller bundled mode """
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    else:
        base_path = os.path.abspath(".")  # Current working directory during development
    return os.path.join(base_path, relative_path)

def browse_file():
    """ Function to browse for a log file """
    Tk().withdraw()  # Hide the main tkinter window
    file_path = askopenfilename(
        title="Select a log file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return file_path

def prompt_save_file(default_name):
    """ Function to prompt the user to save the analysis results """
    Tk().withdraw()  # Hide the main tkinter window
    save = messagebox.askyesno("Save File", "The file was analyzed successfully. Do you want to save the results?")
    if save:
        file_path = asksaveasfilename(
            title="Save Analysis As",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        return file_path
    else:
        return None

def search_errors(log_file, error_data):
    """ Function to search for errors in the log file """
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
    """ Main function to execute the log file analysis """
    json_file_path = resource_path('keywords.json')  # Locate the JSON file
    try:
        with open(json_file_path, 'r') as f:
            error_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the file 'keywords.json' at {json_file_path}.")
        return

    log_file_path = browse_file()
    if not log_file_path:
        print("No file selected. Exiting...")
        return

    log_file_name = os.path.splitext(os.path.basename(log_file_path))[0]
    current_date = datetime.now().strftime("%Y-%m-%d")
    default_output_name = f"{log_file_name}_analysis_{current_date}.txt"

    output_file_path = prompt_save_file(default_output_name)
    if output_file_path is None:
        print("No save location selected. Exiting...")
        return

    found_errors_line, unique_lines_per_error, new_errors = search_errors(log_file_path, error_data)

    with open(output_file_path, 'w') as output_file:
        def write_and_print(line):
            print(line)
            output_file.write(line + '\n')

        write_and_print("\nError Analysis:\n")

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

    print(f"\nAnalysis complete. Results saved to {output_file_path}")

if __name__ == "__main__":
    main()
