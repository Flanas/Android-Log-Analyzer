import os
import sys
from LogAutomation import main as log_automation_main
from LogFolderAutomation import main as log_folder_automation_main

def main_menu():
    while True:
        print("\n===== Log Automation Menu =====")
        print("1. Analyze a single log file")
        print("2. Analyze multiple log files in a folder")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            log_automation_main()
        elif choice == '2':
            log_folder_automation_main()
        elif choice == '0':
            print("Exiting the program.")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()