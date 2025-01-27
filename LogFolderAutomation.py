import json
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
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


def choose_save_location():
    Tk().withdraw()  # Hide the main tkinter window
    folder_path = askdirectory(title="Select a location to save the analysis folder")
    return folder_path


def create_analysis_folder(base_path, folder_name):
    current_date = datetime.now().strftime("%Y-%m-%d")
    consolidated_folder_name = f"{folder_name}_ConsolidatedReport_{current_date}"
    full_path = os.path.join(base_path, consolidated_folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path


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


def save_priority_report(file_data, folder_name, analysis_folder):
    current_date = datetime.now().strftime("%Y-%m-%d")
    priority_file_name = os.path.join(analysis_folder, f"{folder_name}_ReportSummary_{current_date}.txt")

    sorted_files = sorted(file_data.items(), key=lambda x: x[1]['Crashed'], reverse=True)

    with open(priority_file_name, 'w') as priority_file:
        priority_file.write(f"Priority Analysis Report\n")
        priority_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        priority_file.write(f"Folder: {folder_name}\n")
        priority_file.write("=" * 500 + "\n")

        for file_name, data in sorted_files:
            priority_file.write(f"File: {file_name}\n")
            priority_file.write("_" * 50 + "\n")
            priority_file.write(f"  Crashed Errors: {data['Crashed']}\n")
            priority_file.write(f"  New Errors: {data['New Errors']}\n")
            priority_file.write(f"  Known Errors: {data['Known Errors']}\n\n")
            priority_file.write("=" * 50 + "\n\n")

    print(f"Priority report saved to {priority_file_name}")


def main(folder_path=None, save_path=None):
    json_file_path = resource_path('keywords.json')  # Locate the JSON file
    try:
        with open(json_file_path, 'r') as f:
            error_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the file 'keywords.json' at {json_file_path}.")
        return

    # If folder_path is not provided, prompt the user to select a folder
    if folder_path is None:
        folder_path = browse_folder()
        if not folder_path:
            print("No folder selected. Exiting...")
            return

    # Validate that folder_path is a valid directory
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory. Exiting...")
        return

    # Extract the folder name from the folder_path
    folder_name = os.path.basename(folder_path)

    # If save_path is not provided, prompt the user to select a save location
    if save_path is None:
        save_path = choose_save_location()
        if not save_path:
            print("No save location selected. Exiting...")
            return

    # Validate that save_path is a valid directory
    if not os.path.isdir(save_path):
        print(f"Error: '{save_path}' is not a valid directory. Exiting...")
        return

    # Create an analysis folder in the save location
    analysis_folder = create_analysis_folder(save_path, folder_name)

    # Find all .txt files in the selected folder
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    if not txt_files:
        print("No .txt files found in the selected folder. Exiting...")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file_path = os.path.join(analysis_folder, f"{folder_name}_ExceptionAnalysis_{current_date}.txt")

    file_error_data = {}

    # Write the analysis to the output file
    with open(output_file_path, 'w') as output_file:
        def write_and_print(line):
            print(line)
            output_file.write(line + '\n')

        write_and_print(f"Consolidated Error Analysis Report\n")
        write_and_print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        write_and_print(f"Folder: {folder_path}\n")
        write_and_print("=" * 500 + "\n")

        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)
            write_and_print(f"Analyzing File: {file_name}\n")
            write_and_print("=" * 500)

            found_errors_line, unique_lines_per_error, crashed_occurrences = search_errors(file_path, error_data)

            file_error_data[file_name] = {
                "Crashed": found_errors_line.get("Crashed", {}).get("count", 0),
                "New Errors": sum([found_errors_line[et]["count"] for et in found_errors_line if et != "Crashed"]),
                "Known Errors": len(unique_lines_per_error)
            }

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

            write_and_print("=" * 500 + "\n")

    save_priority_report(file_error_data, folder_name, analysis_folder)
    print(f"\nAnalysis complete. Consolidated report saved to {output_file_path}")

    print(f"Folder Path: {folder_path}")
    print(f"Save Path: {save_path}")


if __name__ == "__main__":
    main()
