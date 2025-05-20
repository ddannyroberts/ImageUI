import sys
import os
from PIL import Image
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent, QKeyEvent, QKeySequence, QIntValidator, QShortcut
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal


class ResizeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, image_infos, width, height, percent, base_dir):
        super().__init__()
        self.image_infos = image_infos
        self.width = width
        self.height = height
        self.percent = percent
        self.base_dir = base_dir

    def run(self):
        try:
            total = len(self.image_infos)
            if total == 0:
                self.finished.emit("No images to process.")
                return

            folder_name = os.path.basename(self.base_dir.rstrip("/"))
            output_base = os.path.join(os.path.expanduser("~/Documents"), "ImageResizerOutput")

            fixed_output = os.path.join(output_base, f"{folder_name}_{self.width}x{self.height}")
            percent_output = os.path.join(output_base, f"{folder_name}_{self.percent}%")

            for i, (abs_path, rel_path) in enumerate(self.image_infos):
                img = Image.open(abs_path)
                filename = os.path.basename(abs_path)

                # Fixed resize
                fixed_dir = os.path.join(fixed_output, os.path.dirname(rel_path))
                os.makedirs(fixed_dir, exist_ok=True)
                img.resize((self.width, self.height)).save(os.path.join(fixed_dir, filename))

                # Percent resize
                percent_dir = os.path.join(percent_output, os.path.dirname(rel_path))
                os.makedirs(percent_dir, exist_ok=True)
                pw = int(img.width * self.percent / 100)
                ph = int(img.height * self.percent / 100)
                img.resize((pw, ph)).save(os.path.join(percent_dir, filename))

                self.progress.emit(int((i + 1) / total * 100))

            self.finished.emit(
                f"✅ Saved {total} images to:\n{fixed_output}\n{percent_output}"
            )
        except Exception as e:
            self.finished.emit(f"❌ Error: {str(e)}")


class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer")
        self.setGeometry(100, 100, 600, 600)
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout()

        self.label = QLabel("Browse or Drag & Drop images or folders:")
        self.layout.addWidget(self.label)

        browse_layout = QHBoxLayout()
        self.choose_file_button = QPushButton("Browse Image")
        self.choose_file_button.clicked.connect(self.choose_file)
        browse_layout.addWidget(self.choose_file_button)

        self.choose_folder_button = QPushButton("Browse Folder")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        browse_layout.addWidget(self.choose_folder_button)
        self.layout.addLayout(browse_layout)

        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(64, 64))
        self.image_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.image_list)

        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected Images")
        self.delete_button.clicked.connect(self.delete_selected_images)
        button_layout.addWidget(self.delete_button)

        self.delete_all_button = QPushButton("Delete All Images")
        self.delete_all_button.clicked.connect(self.delete_all_images)
        button_layout.addWidget(self.delete_all_button)

        self.undo_button = QPushButton("Undo Delete")
        self.undo_button.clicked.connect(self.undo_delete)
        button_layout.addWidget(self.undo_button)
        self.layout.addLayout(button_layout)

        size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height")
        self.percent_input = QLineEdit()
        self.percent_input.setPlaceholderText("Percent %")
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(self.height_input)
        size_layout.addWidget(self.percent_input)
        self.layout.addLayout(size_layout)

        int_validator = QIntValidator(1, 10000)
        self.width_input.setValidator(int_validator)
        self.height_input.setValidator(int_validator)
        self.percent_input.setValidator(QIntValidator(1, 500))

        input_style = "color: white; background-color: #1e1e1e; border: 1px solid gray; padding: 2px;"
        for field in [self.width_input, self.height_input, self.percent_input]:
            field.setStyleSheet(input_style)

        self.start_button = QPushButton("Resize Images")
        self.start_button.clicked.connect(self.resize_images)
        self.layout.addWidget(self.start_button)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)

        self.base_dir = ""
        self.image_infos = []
        self.undo_stack = []

        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    def validate_inputs(self):
        valid = True
        error_style = "color: white; background-color: #2a0000; border: 2px solid #ff4c4c; padding: 2px;"
        ok_style = "color: white; background-color: #1e1e1e; border: 1px solid gray; padding: 2px;"
        for field in [self.width_input, self.height_input, self.percent_input]:
            if not field.text().strip():
                field.setStyleSheet(error_style)
                valid = False
            else:
                field.setStyleSheet(ok_style)
        return valid

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.base_dir = os.path.dirname(file_path)
            rel_path = os.path.basename(file_path)
            if file_path not in [p for p, _ in self.image_infos]:
                self.image_infos.append((file_path, rel_path))
            self.load_image_list()

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Choose Folder")
        if folder_path:
            self.base_dir = folder_path
            self.add_images_from_folder(folder_path)
            self.load_image_list()

    def add_images_from_folder(self, folder):
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, start=self.base_dir)
                    if abs_path not in [p for p, _ in self.image_infos]:
                        self.image_infos.append((abs_path, rel_path))

    def load_image_list(self):
        self.image_list.clear()
        for abs_path, _ in self.image_infos:
            pixmap = QPixmap(abs_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
            item = QListWidgetItem(QIcon(pixmap), os.path.basename(abs_path))
            item.setData(Qt.ItemDataRole.UserRole, abs_path)
            self.image_list.addItem(item)

    def delete_selected_images(self):
        removed = []
        for item in self.image_list.selectedItems():
            abs_path = item.data(Qt.ItemDataRole.UserRole)
            removed += [(p, r) for (p, r) in self.image_infos if p == abs_path]
            self.image_infos = [(p, r) for (p, r) in self.image_infos if p != abs_path]
            self.image_list.takeItem(self.image_list.row(item))
        if removed:
            self.undo_stack.append(removed)

    def delete_all_images(self):
        if self.image_infos:
            self.undo_stack.append(self.image_infos.copy())
            self.image_infos = []
            self.image_list.clear()

    def undo_delete(self):
        if self.undo_stack:
            restored = self.undo_stack.pop()
            existing_paths = [p for p, _ in self.image_infos]
            for info in restored:
                if info[0] not in existing_paths:
                    self.image_infos.append(info)
            self.load_image_list()

    def resize_images(self):
        if not self.image_infos:
            QMessageBox.warning(self, "Error", "No images to resize.")
            return
        if not self.validate_inputs():
            QMessageBox.warning(self, "Error", "All input fields are required.")
            return
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            percent = int(self.percent_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numbers.")
            return

        self.progress.setValue(0)
        self.result_label.setText("")

        self.worker = ResizeWorker(self.image_infos, width, height, percent, self.base_dir)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, result):
        self.result_label.setText(result)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.base_dir = path
                self.add_images_from_folder(path)
            elif os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                self.base_dir = os.path.dirname(path)
                rel_path = os.path.basename(path)
                if path not in [p for p, _ in self.image_infos]:
                    self.image_infos.append((path, rel_path))
        self.load_image_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizer()
    window.show()
    sys.exit(app.exec())
