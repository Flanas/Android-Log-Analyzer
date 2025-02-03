import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def rename_and_copy_files():
    """Renames files inside each subfolder and copies them to a new directory."""
    
    # Open a folder selection dialog for the master folder
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    master_folder = filedialog.askdirectory(title="Select Master Folder")

    if not master_folder:
        print("No folder selected. Exiting...")
        return

    # Get the master folder's name
    master_folder_name = os.path.basename(master_folder)
    
    # Create the output directory
    renamed_folder = f"{master_folder}_Renamed"
    os.makedirs(renamed_folder, exist_ok=True)

    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Iterate through each subfolder
    for subfolder in os.listdir(master_folder):
        subfolder_path = os.path.join(master_folder, subfolder)

        if os.path.isdir(subfolder_path):  # Process only directories
            print(f"Processing subfolder: {subfolder}")

            # Iterate over files in subfolder
            for filename in os.listdir(subfolder_path):
                old_file_path = os.path.join(subfolder_path, filename)

                if filename == "app.txt":
                    # Rename app.txt with today's date
                    new_filename = f"{subfolder}.{today_date}.txt"
                elif filename.startswith("app.") and filename.endswith(".txt"):
                    # Rename other app.*.txt files
                    new_filename = filename.replace("app.", f"{subfolder}.", 1)
                else:
                    print(f"Skipping file (does not match pattern): {filename}")
                    continue

                new_file_path = os.path.join(renamed_folder, new_filename)

                # Copy the renamed file to the new directory
                shutil.copy2(old_file_path, new_file_path)
                print(f'Copied & Renamed: "{filename}" → "{new_filename}"')

    print("Processing completed! All files are stored in:", renamed_folder)

def main():
    """Main function to initiate file processing."""
    rename_and_copy_files()

if __name__ == "__main__":
    main()