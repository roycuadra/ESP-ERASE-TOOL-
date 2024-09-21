import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPalette, QLinearGradient, QColor
from PyQt5.QtCore import Qt

class ESPToolGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP ERASE TOOL")
        self.setGeometry(100, 100, 300, 200)

        icon_path = os.path.join(os.path.dirname(__file__), 'micro.ico')  # Use .ico file
        self.setWindowIcon(QIcon(icon_path))

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
        footer = QLabel("Created by Roy Cuadra @ 2024")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:lightgray;")  # Set footer color to gray
        layout.addWidget(footer)

        # Set layout to the main window
        self.setLayout(layout)

    def set_auto_gradient(self):
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0, QColor(40, 40, 40))  # Dark color
        gradient.setColorAt(1, QColor(70, 70, 70))  # Lighter dark color

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
        """)  # Keep your existing button styling here
        button.clicked.connect(callback)
        return button

    def execute_esptool(self, command):
        try:
            # Open a command prompt window and execute the specified command
            subprocess.Popen(['cmd', '/k', 'python', '-m', 'esptool'] + command, shell=True)
        except Exception as e:
            # Display an error message if the command fails
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ESPToolGUI()
    window.show()
    sys.exit(app.exec_())
