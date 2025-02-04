import os
import shutil
from datetime import datetime

def rename_and_copy_files(master_folder, save_path):
    """
    Renames files inside each subfolder and copies them to a new directory.
    
    Args:
        master_folder (str): Path to the master folder containing subfolders with files.
        save_path (str): Path to the folder where renamed files will be saved.
    """
    if not master_folder or not save_path:
        print("No master folder or save path provided. Exiting...")
        return

    # Get the master folder's name
    master_folder_name = os.path.basename(master_folder)
    
    # Create the output directory
    renamed_folder = os.path.join(save_path, f"{master_folder_name}_Renamed")
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

def main(master_folder=None, save_path=None):
    """
    Main function to initiate file processing.
    
    Args:
        master_folder (str): Path to the master folder containing subfolders with files.
        save_path (str): Path to the folder where renamed files will be saved.
    """
    if not master_folder or not save_path:
        print("No master folder or save path provided. Exiting...")
        return

    rename_and_copy_files(master_folder, save_path)

if __name__ == "__main__":
    # For standalone execution, use the original tkinter folder selection
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    master_folder = filedialog.askdirectory(title="Select Master Folder")
    save_path = filedialog.askdirectory(title="Select Folder to Save Renamed Files")

    if master_folder and save_path:
        main(master_folder, save_path)
    else:
        print("No master folder or save path selected. Exiting...")