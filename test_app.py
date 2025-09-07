import sys
from PyQt6.QtWidgets import QApplication
from main import ImageResizeApp

def test_app_opens(qtbot):
    app = QApplication.instance() or QApplication(sys.argv)
    window = ImageResizeApp()
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()
