import os
import sys
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
)
from PyQt6.QtGui import (
    QIntValidator,
)
from PyQt6.QtCore import (
    Qt,
    QThread,
    QObject,
    pyqtSignal,
)

class ResizeProcess(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, base_dir, villa_name, images, width, height, percent):
        super().__init__()
        self.base_dir = base_dir
        self.villa_name = villa_name
        self.images = images
        self.width = width
        self.height = height
        self.percent = percent

    def resize_work(self):
        try:
            self.output_folder = os.path.join("~", "Pictures", "ImageResizerOutput")
            # Expand ~ to full name like /Users/<your uesrname> (macOS)
            self.full_output_folder = os.path.expanduser(self.output_folder)
            # If not have ~/Documents/ImageResizeOutput folder create it
            if not os.path.isdir(self.full_output_folder):
                os.makedirs(self.full_output_folder, exist_ok=True)

            self.folder_original_output = os.path.join(self.full_output_folder, f"{self.villa_name}_High Res")
            self.folder_dimension_output = os.path.join(self.full_output_folder, f"{self.villa_name}_Resize")
            self.folder_percent_output = os.path.join(self.full_output_folder, f"{self.villa_name}_Low Res")

            if not os.path.isdir(self.folder_original_output):
                os.makedirs(self.folder_original_output, exist_ok=True)
            if self.width is not None and self.height is not None:
                if not os.path.isdir(self.folder_dimension_output):
                    os.makedirs(self.folder_dimension_output, exist_ok=True)
            if self.percent is not None:
                if not os.path.isdir(self.folder_percent_output):
                    os.makedirs(self.folder_percent_output, exist_ok=True)


            total = len(self.images)
            folder_counts = {}
            if total == 0:
                self.finished.emit("No images to process")
                return

            for i, (dir_name, file_name) in enumerate(self.images):
                dir_original_output = os.path.join(self.folder_original_output, dir_name)
                dir_dimension_output = os.path.join(self.folder_dimension_output, dir_name)
                dir_percent_output = os.path.join(self.folder_percent_output, dir_name)
                file_extension = os.path.splitext(file_name)[1]

                if dir_name not in folder_counts:
                    folder_counts[dir_name] = 1
                else:
                    folder_counts[dir_name] += 1
                count = str(folder_counts[dir_name]).zfill(2)

                if not os.path.isdir(dir_original_output):
                    os.makedirs(dir_original_output, exist_ok=True)
                original_img = Image.open(os.path.join(self.base_dir, dir_name, file_name))
                original_img.save(os.path.join(self.folder_original_output, dir_name, f"{self.villa_name}_{dir_name}_{count}{file_extension}"))

                if self.width is not None and self.height is not None:
                    if not os.path.isdir(dir_dimension_output):
                        os.makedirs(dir_dimension_output, exist_ok=True)
                    resize_img_dimension = original_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    resize_img_dimension.save(os.path.join(self.folder_dimension_output, dir_name, f"{self.villa_name}_{dir_name}_{count}{file_extension}"))

                if self.percent is not None:
                    if not os.path.isdir(dir_percent_output):
                        os.makedirs(dir_percent_output, exist_ok=True)
                    resize_img_percent = original_img.resize((int(original_img.width * self.percent / 100), int(original_img.height * self.percent / 100)), Image.Resampling.LANCZOS)
                    resize_img_percent.save(os.path.join(self.folder_percent_output, dir_name, f"{self.villa_name}_{dir_name}_{count}{file_extension}"))

                self.progress.emit(int((i + 1) / total * 100))

            self.finished.emit(f"Save images to:\n{self.full_output_folder}")

        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")
            return


class ImageResizeApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer")

        browse_button_layout = QHBoxLayout()

        self.browse_folder_button = QPushButton("Browse Folder")
        self.browse_folder_button.clicked.connect(self.browse_folder_cilck)
        browse_button_layout.addWidget(self.browse_folder_button)

        self.image_infos = []
        self.base_dir = ''
        self.villa_name = os.path.basename(self.base_dir)

        ##### Input Layout #####
        input_field_layout = QVBoxLayout()
        input_dimension_filed_layout = QHBoxLayout()
        input_percent_filed_layout = QHBoxLayout()

        # Width Input
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("width (1 - 10000)")
        self.width_input.setValidator(QIntValidator(1,10000))

        # Height Input
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("height (1 - 10000)")
        self.height_input.setValidator(QIntValidator(1,10000))

        # Width x Height Input Layout
        input_dimension_filed_layout.addWidget(self.width_input)
        input_dimension_filed_layout.addWidget(QLabel("x"))
        input_dimension_filed_layout.addWidget(self.height_input)

        # Percent
        self.percent_input = QLineEdit()
        self.percent_input.setPlaceholderText("percent (1 - 500)")
        self.percent_input.setValidator(QIntValidator(1,500))

        # Percent Input Layout
        input_percent_filed_layout.addWidget(self.percent_input)
        input_percent_filed_layout.addWidget(QLabel("%"))

        input_field_layout.addLayout(input_dimension_filed_layout)
        input_field_layout.addLayout(input_percent_filed_layout)

        self.villa_label = QLabel(f"Name: {self.villa_name}")
        self.villa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_click)

        self.delete_all_button = QPushButton("Delete All")
        self.delete_all_button.clicked.connect(self.delete_all_click)

        self.image_list_widget = QListWidget()
        self.image_list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        ##### Progress Bar #####
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        ##### Result Label #####
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ##### Main Layout #####
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_field_layout)
        main_layout.addWidget(self.villa_label)
        main_layout.addWidget(self.image_list_widget)
        main_layout.addLayout(browse_button_layout)
        main_layout.addWidget(self.delete_all_button)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)

    def browse_folder_cilck(self):
        folder_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select From Folder"
        )
        if folder_path:
            image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        subfolder_name = os.path.basename(root)

                        item = QListWidgetItem(f"{subfolder_name} / {file}")
                        item.setData(Qt.ItemDataRole.UserRole, (subfolder_name, file))

                        self.image_infos.append((subfolder_name, file))
                        self.image_list_widget.addItem(item)

            if self.image_infos:
                self.base_dir = folder_path
                self.villa_name = os.path.basename(self.base_dir)
                self.villa_label.setText(f"Name: {self.villa_name}")

    def start_click(self):
        # Validate input text
        if not self.width_input.text() and not self.height_input.text() and not self.percent_input.text():
            QMessageBox.warning(
                self,
                "Error",
                "Please enter numbers."
            )
            return

        if not self.percent_input.text():
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            percent = None
        elif not self.width_input.text() and not self.height_input.text():
            width = None
            height = None
            percent = int(self.percent_input.text())
        else:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            percent = int(self.percent_input.text())

        self.resize_thread = QThread()
        self.resize_process = ResizeProcess(self.base_dir, self.villa_name, self.image_infos, width, height, percent)
        self.resize_process.moveToThread(self.resize_thread)

        self.resize_thread.started.connect(self.resize_process.resize_work)

        self.progress_bar.setValue(0)
        self.resize_process.progress.connect(self.progress_bar.setValue)

        self.resize_process.finished.connect(self.on_finished)

        self.resize_thread.start()

    def on_finished(self, result):
        self.result_label.setText(result)

        self.villa_name = ""
        self.villa_label.setText(f"Name: {self.villa_name}")
        self.image_infos.clear()
        self.image_list_widget.clear()

        self.resize_thread.quit()
        self.resize_thread.wait()

    def delete_all_click(self):
        self.villa_name = ""
        self.villa_label.setText(f"Name: {self.villa_name}")

        self.image_list_widget.clear()
        self.image_infos.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizeApp()
    window.show()
    sys.exit(app.exec())
