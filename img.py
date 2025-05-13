import sys
import os
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class ResizeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, image_path, width, height):
        super().__init__()
        self.image_path = image_path
        self.width = width
        self.height = height

    def run(self):
        try:
            img = Image.open(self.image_path)
            filename = os.path.basename(self.image_path)
            name, ext = os.path.splitext(filename)

            resized_img = img.resize((self.width, self.height))
            resized_half = img.resize((self.width // 2, self.height // 2))

            os.makedirs("output", exist_ok=True)
            output1 = os.path.join("output", f"{name}_resized{ext}")
            output2 = os.path.join("output", f"{name}_resized_half{ext}")

            resized_img.save(output1)
            resized_half.save(output2)

            self.progress.emit(100)
            self.finished.emit(f"Saved:\n- {output1}\n- {output2}")
        except Exception as e:
            self.finished.emit(str(e))


class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer (Double Output)")
        self.setGeometry(100, 100, 400, 250)

        self.layout = QVBoxLayout()

        self.label = QLabel("Choose an image:")
        self.layout.addWidget(self.label)

        self.choose_button = QPushButton("Browse")
        self.choose_button.clicked.connect(self.choose_file)
        self.layout.addWidget(self.choose_button)

        size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height")
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(self.height_input)
        self.layout.addLayout(size_layout)

        self.start_button = QPushButton("Resize Image")
        self.start_button.clicked.connect(self.resize_image)
        self.layout.addWidget(self.start_button)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)
        self.image_path = None

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")

    def resize_image(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please choose an image.")
            return

        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Width and height must be integers.")
            return

        self.progress.setValue(0)
        self.result_label.setText("")

        self.worker = ResizeWorker(self.image_path, width, height)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, result):
        self.result_label.setText(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizer()
    window.show()
    sys.exit(app.exec())
