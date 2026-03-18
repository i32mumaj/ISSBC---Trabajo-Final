import sys
from PyQt6.QtWidgets import QApplication

from model.model import Model
from view.view import MainWindow
from controller.controller import Controller


def main():
    app = QApplication(sys.argv)

    model = Model()
    view = MainWindow()
    controller = Controller(model, view)

    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()