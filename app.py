import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMenuBar,
    QFileDialog, QComboBox, QLineEdit, QHBoxLayout, QMainWindow, QDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PIL import Image

# Settings File Path
SETTINGS_FILE = Path.home() / ".image_converter_settings.json"

# Function to load settings
def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    else:
        return {"default_save_path": str(Path.home() / "Downloads")}

# Function to save settings
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(400, 400, 300, 100)

        layout = QVBoxLayout()

        # Save location path input
        self.save_location_label = QLabel("Default Save Location:")
        self.save_location_input = QLineEdit(load_settings().get("default_save_path", str(Path.home() / "Downloads")))
        self.save_location_btn = QPushButton("Browse")
        self.save_location_btn.clicked.connect(self.set_save_location)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.save_location_input)
        location_layout.addWidget(self.save_location_btn)

        layout.addWidget(self.save_location_label)
        layout.addLayout(location_layout)

        # Save Button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def set_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Default Save Location")
        if directory:
            self.save_location_input.setText(directory)

    def save_settings(self):
        # Save the new default save path to the settings file
        settings = {"default_save_path": self.save_location_input.text()}
        save_settings(settings)
        self.accept()

class ImageConverter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load settings
        self.settings = load_settings()

        # Set up the main UI layout
        self.setWindowTitle("ImageFlow - Image Converter")
        self.setGeometry(300, 300, 500, 300)

        # Create menu bar with Settings option
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Preferences")
        settings_action.triggered.connect(self.open_settings_dialog)

        # Central widget for main UI elements
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Label for Drag and Drop
        self.drag_drop_label = QLabel("Drag and Drop Images Here or Select Files")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.drag_drop_label.setStyleSheet("QLabel { border: 2px dashed #008CBA; padding: 40px; background-color: #f0f0f0; color: #333; }")
        layout.addWidget(self.drag_drop_label)

        # Set up drag and drop support
        self.setAcceptDrops(True)

        # File Select Button
        self.select_file_btn = QPushButton("Select Image Files")
        self.select_file_btn.setStyleSheet("QPushButton { background-color: #008CBA; color: white; padding: 8px 16px; border-radius: 5px; } QPushButton:hover { background-color: #0079a1; }")
        self.select_file_btn.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_file_btn)

        # Conversion format selection
        format_layout = QHBoxLayout()
        self.format_label = QLabel("Select Output Format:")
        self.format_selector = QComboBox()
        self.format_selector.addItems(["JPEG", "PNG", "BMP", "TIFF", "GIF", "WEBP"])

        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_selector)
        layout.addLayout(format_layout)

        # Default save location (loaded from settings)
        save_location_layout = QHBoxLayout()
        self.save_location_label = QLabel("Save Location:")
        self.save_location_input = QLineEdit(self.settings.get("default_save_path"))
        self.save_location_btn = QPushButton("Change")
        self.save_location_btn.setStyleSheet("QPushButton { background-color: #008CBA; color: white; padding: 5px 10px; border-radius: 5px; } QPushButton:hover { background-color: #0079a1; }")
        self.save_location_btn.clicked.connect(self.set_save_location)

        save_location_layout.addWidget(self.save_location_label)
        save_location_layout.addWidget(self.save_location_input)
        save_location_layout.addWidget(self.save_location_btn)
        layout.addLayout(save_location_layout)

        # Convert Button
        self.convert_btn = QPushButton("Convert Images")
        self.convert_btn.setStyleSheet("QPushButton { background-color: #008CBA; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #0079a1; }")
        self.convert_btn.clicked.connect(self.convert_images)
        layout.addWidget(self.convert_btn)

        # Placeholder for file paths
        self.image_paths = []

    # Open the Settings dialog
    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_():  # Reload settings if changes were saved
            self.settings = load_settings()
            self.save_location_input.setText(self.settings.get("default_save_path"))

    # Drag and Drop Events for multiple files
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        self.image_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        self.drag_drop_label.setText(f"{len(self.image_paths)} files selected")

    # File Dialog for selecting multiple images
    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Image Files", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp)")
        if file_paths:
            self.image_paths = file_paths
            self.drag_drop_label.setText(f"{len(self.image_paths)} files selected")

    # Set save location
    def set_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if directory:
            self.save_location_input.setText(directory)

    # Batch Image Conversion with Success and Error Dialogs
    def convert_images(self):
        if not self.image_paths:
            self.drag_drop_label.setText("Please select one or more images first!")
            return

        # Get selected format
        output_format = self.format_selector.currentText().lower()
        save_dir = Path(self.save_location_input.text()).resolve()

        # Ensure save directory exists
        if not save_dir.exists():
            try:
                save_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create directory: {e}")
                return

        # Batch conversion process
        success_count = 0
        failed_files = []

        for image_path in self.image_paths:
            base_name = Path(image_path).stem
            output_path = save_dir / f"{base_name}.{output_format}"

            try:
                # Open and convert each image
                with Image.open(image_path) as image:
                    if output_format == "webp":
                        image.save(output_path, format=output_format.upper(), lossless=True)
                    else:
                        image.save(output_path, format=output_format.upper(), quality=100)
                success_count += 1
            except Exception as e:
                failed_files.append(str(image_path))

        # Show success or error dialog based on results
        if failed_files:
            error_message = f"Failed to convert {len(failed_files)} out of {len(self.image_paths)} images:\n" + "\n".join(failed_files)
            QMessageBox.critical(self, "Conversion Errors", error_message)
        else:
            QMessageBox.information(self, "Success", f"Successfully converted {success_count} images.")

# Main application loop
app = QApplication(sys.argv)
window = ImageConverter()
window.show()
sys.exit(app.exec_())
