import sys
import os
import subprocess
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPalette, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ESPToolGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP ERASE TOOL")
        self.setGeometry(100, 100, 300, 200)

        # Set icon with a fallback if the file is missing
        icon_path = os.path.join(os.path.dirname(__file__), 'micro.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Warning: Icon file 'micro.ico' not found. Proceeding without an icon.")

        # Set gradient background
        self.set_auto_gradient()

        # Create layout
        layout = QVBoxLayout()

        # Create and configure buttons
        button_esptool = self.create_button("Execute ESPTool", lambda: self.execute_esptool([]))
        layout.addWidget(button_esptool)

        button_esp8266 = self.create_button("Execute ESP8266", lambda: self.execute_esptool(['--chip', 'esp8266', 'erase_flash']))
        layout.addWidget(button_esp8266)

        button_esp32 = self.create_button("Execute ESP32", lambda: self.execute_esptool(['--chip', 'esp32', 'erase_flash']))
        layout.addWidget(button_esp32)

        # Create and add footer
        footer = QLabel("Version 1.1")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:lightgray;")
        layout.addWidget(footer)

        # Set layout to the main window
        self.setLayout(layout)

    def set_auto_gradient(self):
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0, QColor(40, 40, 40))
        gradient.setColorAt(1, QColor(70, 70, 70))

        palette = QPalette()
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("""
         QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                                        stop: 0 #007BFF, stop: 1 #0056b3); 
            color: white;
            border: none;  
            padding: 10px;
            font-size: 16px;
            border-radius: 24px; 
            min-width: 150px;     
            min-height: 40px;     
            max-width: 300px;     
            max-height: 50px;     
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                                        stop: 0 #0056b3, stop: 1 #003d7a);  
        }
        QPushButton:pressed {
            background: #003d7a;  
        }
        """)
        button.clicked.connect(callback)
        return button

    def find_python_executable(self):
        """ Find the correct Python executable (python or python3) """
        for python_cmd in ['python', 'python3']:
            try:
                if subprocess.call([python_cmd, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    return python_cmd
            except FileNotFoundError:
                pass
        return None

    def execute_esptool(self, command):
        python_cmd = self.find_python_executable()
        if python_cmd is None:
            response = QMessageBox.question(
                self, "Python Not Found",
                "Python is not installed or not in the system PATH. Would you like to go to the Python website to download it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                # Open Python website in the user's default web browser
                webbrowser.open('https://www.python.org/downloads/')
            return

        # Run the esptool commands asynchronously to avoid blocking the GUI
        self.thread = ExecuteCommandThread(python_cmd, command, self)
        self.thread.command_output.connect(self.show_command_output)
        self.thread.start()

    def show_command_output(self, output):
        if output["type"] == "error":
            QMessageBox.critical(self, "Error", output["message"])
        elif output["type"] == "info":
            QMessageBox.information(self, "Info", output["message"])


class ExecuteCommandThread(QThread):
    command_output = pyqtSignal(dict)

    def __init__(self, python_cmd, command, parent=None):
        super().__init__(parent)
        self.python_cmd = python_cmd
        self.command = command

    def run(self):
        try:
            # Check if pip is installed
            pip_installed = subprocess.call([self.python_cmd, '-m', 'pip', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
            if not pip_installed:
                self.command_output.emit({"type": "info", "message": "pip is not installed. Installing pip now."})
                subprocess.call([self.python_cmd, '-m', 'ensurepip'])

            # Check if esptool is installed, and install it if necessary
            esptool_installed = subprocess.call([self.python_cmd, '-m', 'esptool', '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
            if not esptool_installed:
                self.command_output.emit({"type": "info", "message": "esptool is not installed. Installing esptool now."})
                subprocess.call([self.python_cmd, '-m', 'pip', 'install', '--user', 'esptool'])

            # Execute the esptool command
            subprocess.Popen([self.python_cmd, '-m', 'esptool'] + self.command)

        except Exception as e:
            self.command_output.emit({"type": "error", "message": f"An error occurred: {str(e)}"})


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ESPToolGUI()
    window.show()
    sys.exit(app.exec_())
