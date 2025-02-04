import os
from datetime import datetime

def rename_files_in_folder(folder_path, save_path):
    """
    Renames text files in the specified folder based on specific rules and saves them to the specified save_path.
    
    Args:
        folder_path (str): Path to the folder containing the text files.
        save_path (str): Path to the folder where renamed files will be saved.
    """
    if not folder_path or not save_path:
        print("No folder or save path provided. Exiting...")
        return

    # Get the folder name
    folder_name = os.path.basename(folder_path)
    print(f"Selected folder: {folder_name}")

    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Today's date: {today_date}")

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        print(f"Processing file: {filename}")

        if filename == "app.txt":
            # Rename to "foldername.YYYY-MM-DD.txt"
            new_filename = f"{folder_name}.{today_date}.txt"
            print(f"Renaming 'app.txt' to: {new_filename}")

        elif filename.startswith("app.") and filename.endswith(".txt"):
            # Replace "app." with the folder name
            new_filename = filename.replace("app.", f"{folder_name}.", 1)
            print(f"Renaming 'app.*.txt' to: {new_filename}")

        else:
            print(f"Skipping file (does not match pattern): {filename}")
            continue  # Skip files that don't match the pattern

        # Construct the new file path in the save_path directory
        new_path = os.path.join(save_path, new_filename)

        # Rename and move the file
        os.rename(old_path, new_path)
        print(f'Renamed and moved: "{filename}" → "{new_filename}"')

    print("Renaming completed!")

def main(folder_path=None, save_path=None):
    """
    Main function to call the rename process.
    
    Args:
        folder_path (str): Path to the folder containing the text files.
        save_path (str): Path to the folder where renamed files will be saved.
    """
    if not folder_path or not save_path:
        print("No folder or save path provided. Exiting...")
        return

    rename_files_in_folder(folder_path, save_path)

if __name__ == "__main__":
    # For standalone execution, use the original tkinter folder selection
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Text Files")
    save_path = filedialog.askdirectory(title="Select Folder to Save Renamed Files")

    if folder_path and save_path:
        main(folder_path, save_path)
    else:
        print("No folder or save path selected. Exiting...")