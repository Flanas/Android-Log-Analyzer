import sys
import os
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal
from LogAutomation import main as log_automation_main
from LogFolderAutomation import main as log_folder_automation_main


class AnalysisWorker(QThread):
    progress = pyqtSignal(int)  # Signal to update the progress bar
    finished = pyqtSignal(str)  # Signal when the analysis is complete
    error = pyqtSignal(str)     # Signal when an error occurs

    def __init__(self, folder_path, save_path, log_files):
        super().__init__()
        self.folder_path = folder_path
        self.save_path = save_path
        self.log_files = log_files

    def run(self):
        try:
            total_files = len(self.log_files)
            for index, log_file in enumerate(self.log_files):
                log_file_path = os.path.join(self.folder_path, log_file)
                print(f"Processing file: {log_file_path}")  # Debugging log file path

                # Perform analysis on the current file
                log_folder_automation_main(folder_path=self.folder_path, save_path=self.save_path)

                # Emit progress signal
                self.progress.emit(index + 1)

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
        self.setGeometry(200, 200, 400, 200)

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

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit_program)
        layout.addWidget(btn_exit)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

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

        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)

        def process_single_file():
            try:
                log_automation_main(file_path, save_path)
                self.progress_bar.setValue(100)
                QMessageBox.information(
                    self,
                    "Success",
                    f"The log file was analyzed successfully.\n\nAnalysis report saved to:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            finally:
                self.progress_bar.hide()

        self.timer = QTimer(self)
        self.timer.timeout.connect(process_single_file)
        self.timer.setSingleShot(True)
        self.timer.start(100)

    def analyze_multiple_logs(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Folder Containing Log Files")
        if not folder_path:
            QMessageBox.warning(self, "No Selection", "No folder selected. Please try again.")
            return

        save_path = QFileDialog.getExistingDirectory(self, "Select a Location to Save the Analysis")
        if not save_path:
            QMessageBox.warning(self, "No Location Selected", "No location specified to save the analysis. Returning to the menu.")
            return

        log_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        total_files = len(log_files)

        if total_files == 0:
            QMessageBox.warning(self, "No Files Found", "No log files found in the selected folder.")
            return

        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(total_files)

        # Start analysis worker thread
        self.worker = AnalysisWorker(folder_path, save_path, log_files)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, analysis_path):
        self.progress_bar.hide()
        QMessageBox.information(
            self,
            "Success",
            f"The log files were analyzed successfully.\n\nConsolidated report saved to: {analysis_path}"
        )

    def on_analysis_error(self, error_message):
        self.progress_bar.hide()
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
