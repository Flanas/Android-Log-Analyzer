import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def rename_files_in_folder():
    """Renames text files in a selected folder based on specific rules."""
    
    # Open a folder selection dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Text Files")

    if not folder_path:  # If no folder was selected, exit
        print("No folder selected. Exiting...")
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

        new_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_path, new_path)
        print(f'Renamed: "{filename}" → "{new_filename}"')

    print("Renaming completed!")

def main():
    """Main function to call the rename process."""
    rename_files_in_folder()

if __name__ == "__main__":
    main()