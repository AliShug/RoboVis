import sys

from PyQt5.QtWidgets import QApplication

from com.robovis.window import RVWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RVWindow()
    window.show()
    sys.exit(app.exec_())
