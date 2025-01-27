import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog, QProgressBar
)
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from LogAutomation import main as log_automation_main
from LogFolderAutomation import main as log_folder_automation_main


class LogAutomationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the window
        self.setWindowTitle("Log Automation Menu")
        self.setGeometry(200, 200, 400, 200)

        # Create layout
        layout = QVBoxLayout()

        # Create label
        label = QLabel("===== Log Automation Menu =====")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Create buttons
        btn_single_log = QPushButton("Analyze a single log file")
        btn_single_log.clicked.connect(self.analyze_single_log)
        layout.addWidget(btn_single_log)

        btn_multiple_logs = QPushButton("Analyze multiple log files in a folder")
        btn_multiple_logs.clicked.connect(self.analyze_multiple_logs)
        layout.addWidget(btn_multiple_logs)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit_program)
        layout.addWidget(btn_exit)

        # Add a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)  # Start at 0%
        self.progress_bar.hide()  # Hide the progress bar initially
        layout.addWidget(self.progress_bar)

        # Set layout
        self.setLayout(layout)

    def analyze_single_log(self):
    # Prompt for the log file to analyze
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a Log File", "", "Log Files (*.txt);;All Files (*)")
        if not file_path:
            QMessageBox.warning(self, "No Selection", "No file selected. Please try again.")
            return

    # Extract the base name of the log file (without extension)
        log_file_name = os.path.basename(file_path)  # e.g., "app.txt" or "GGMCL0.txt"
        log_file_base_name = os.path.splitext(log_file_name)[0]  # e.g., "app" or "GGMCL0"

    # Generate the default save file name
        current_date = datetime.now().strftime("%Y-%m-%d")
        default_save_file_name = f"{log_file_base_name}_Analysis_{current_date}.txt"

    # Prompt the user to specify the save location and filename
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Report As",
            os.path.join(os.path.expanduser("~"), default_save_file_name),
            "Text Files (*.txt);;All Files (*)"
        )

        if not save_path:  # Check if the user canceled or did not specify a save location
            QMessageBox.warning(self, "No Save Location", "No save location specified. Please try again.")
            return

    # Show the progress bar
        self.progress_bar.show()
        self.progress_bar.setValue(0)  # Reset progress bar to 0%

    # Simulate progress using a QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_progress(file_path, save_path))
        self.timer.start(100)  # Update progress every 100ms


    def update_progress(self, file_path, save_path):
        # Increment the progress bar
        current_value = self.progress_bar.value()
        if current_value < 100:
            self.progress_bar.setValue(current_value + 10)  # Increment by 10%
        else:
            # Stop the timer when progress reaches 100%
            self.timer.stop()

            # Run the analysis
            try:
                log_automation_main(file_path, save_path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"The log file was analyzed successfully.\n\nAnalysis report saved to:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            finally:
                # Hide the progress bar after analysis is complete
                self.progress_bar.hide()

    def analyze_multiple_logs(self):
        # Prompt for the folder containing log files
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Folder Containing Log Files")
        if not folder_path:  # Check if the user canceled or did not select a folder
            QMessageBox.warning(self, "No Selection", "No folder selected. Please try again.")
            return

        # Prompt for the location to save the analysis results
        save_path = QFileDialog.getExistingDirectory(self, "Select a Location to Save the Analysis")
        if not save_path:  # Check if the user canceled or did not select a folder
            QMessageBox.warning(self, "No Location Selected", "No location specified to save the analysis. Returning to the menu.")
            return

        try:
            log_folder_automation_main(folder_path, save_path)  # Pass both folder_path and save_path
            analysis_folder_name = os.path.basename(folder_path) + f"_ConsolidatedReport_{datetime.now().strftime('%Y-%m-%d')}"
            full_analysis_path = os.path.join(save_path, analysis_folder_name)

            QMessageBox.information(
                self,
                "Success",
                f"The log files were analyzed successfully.\n\nConsolidated report saved to: {full_analysis_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def exit_program(self):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogAutomationUI()
    window.show()
    sys.exit(app.exec_())