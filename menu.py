import sys
import os
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from LogFolderAutomation import main as log_folder_automation_main
from LogAutomation import main as log_automation_main
import Rename  # Import Rename.py module


class AnalysisWorker(QThread):
    finished = pyqtSignal(str)  # Signal when the analysis is complete
    error = pyqtSignal(str)     # Signal when an error occurs

    def __init__(self, folder_path, save_path):
        super().__init__()
        self.folder_path = folder_path
        self.save_path = save_path

    def run(self):
        try:
            # Run LogFolderAutomation directly without iterating files
            log_folder_automation_main(folder_path=self.folder_path, save_path=self.save_path)

            # Emit finished signal with the analysis folder path
            analysis_folder_name = os.path.basename(self.folder_path) + f"_ConsolidatedReport_{datetime.now().strftime('%Y-%m-%d')}"
            full_analysis_path = os.path.join(self.save_path, analysis_folder_name)
            self.finished.emit(full_analysis_path)
        except Exception as e:
            self.error.emit(str(e))


class LogAutomationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Log Automation Menu")
        self.setGeometry(200, 200, 400, 250)

        # Create layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("===== Log Automation Menu =====")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Buttons
        btn_single_log = QPushButton("Analyze a single log file")
        btn_single_log.clicked.connect(self.analyze_single_log)
        layout.addWidget(btn_single_log)

        btn_multiple_logs = QPushButton("Analyze multiple log files in a folder")
        btn_multiple_logs.clicked.connect(self.analyze_multiple_logs)
        layout.addWidget(btn_multiple_logs)

        btn_rename_files = QPushButton("Rename log files in a folder")  # New button
        btn_rename_files.clicked.connect(self.rename_files)  # Connect button to rename function
        layout.addWidget(btn_rename_files)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit_program)
        layout.addWidget(btn_exit)

        # Set layout
        self.setLayout(layout)

    def analyze_single_log(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a Log File", "", "Log Files (*.txt);;All Files (*)")
        if not file_path:
            QMessageBox.warning(self, "No Selection", "No file selected. Please try again.")
            return

        log_file_name = os.path.basename(file_path)
        log_file_base_name = os.path.splitext(log_file_name)[0]
        current_date = datetime.now().strftime("%Y-%m-%d")
        default_save_file_name = f"{log_file_base_name}_Analysis_{current_date}.txt"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Report As",
            os.path.join(os.path.expanduser("~"), default_save_file_name),
            "Text Files (*.txt);;All Files (*)"
        )

        if not save_path:
            QMessageBox.warning(self, "No Save Location", "No save location specified. Please try again.")
            return

        try:
            log_automation_main(file_path, save_path)
            QMessageBox.information(
                self,
                "Success",
                f"The log file was analyzed successfully.\n\nAnalysis report saved to:\n{save_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def analyze_multiple_logs(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Folder Containing Log Files")
        if not folder_path:
            QMessageBox.warning(self, "No Selection", "No folder selected. Please try again.")
            return

        save_path = QFileDialog.getExistingDirectory(self, "Select a Location to Save the Analysis")
        if not save_path:
            QMessageBox.warning(self, "No Location Selected", "No location specified to save the analysis. Returning to the menu.")
            return

        # Create a processing dialog with no buttons initially
        self.processing_dialog = QMessageBox(self)
        self.processing_dialog.setWindowTitle("Analyzing Files")
        self.processing_dialog.setText("Analyzing files: Please wait...")
        self.processing_dialog.setStandardButtons(QMessageBox.NoButton)  # No buttons initially
        self.processing_dialog.show()

        # Start analysis worker thread
        self.worker = AnalysisWorker(folder_path, save_path)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.error.connect(self.processing_dialog.close)  # Close immediately if there's an error
        self.worker.start()

    def rename_files(self):
        """Calls Rename.py to rename files in a selected folder."""
        try:
            Rename.main()
            QMessageBox.information(self, "Success", "Files have been renamed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while renaming files: {e}")

    def on_analysis_finished(self, analysis_path):
        # Show success message
        QMessageBox.information(
            self,
            "Success",
            f"The log files were analyzed successfully.\n\nConsolidated report saved to: {analysis_path}"
        )

        # Now, update the "Analyzing Files" dialog to show a Close button
        self.processing_dialog.setStandardButtons(QMessageBox.Close)
        self.processing_dialog.button(QMessageBox.Close).clicked.connect(self.processing_dialog.close)
        self.processing_dialog.setText("Analysis Complete! Click Close to exit.")

    def on_analysis_error(self, error_message):
        self.processing_dialog.close()  # Close processing dialog immediately on error
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

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
