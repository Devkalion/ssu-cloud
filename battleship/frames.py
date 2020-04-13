import sys

from PySide2.QtCore import QEvent, Qt, QObject
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QGridLayout

from models import Field, Ship, Direction


class PlaceField(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = Field()
        self.layout = QGridLayout()
        internal_layout = QGridLayout()
        self.buttons = {}
        internal_layout.setSpacing(0)

        randomize_btn = QPushButton(text='randomize')
        randomize_btn.clicked.connect(self.randomize_field)
        self.layout.addWidget(randomize_btn, 0, 0)

        for row in range(10):
            for column in range(10):
                button = QPushButton()
                button.setFixedSize(20, 20)
                button.setObjectName(f'{row}_{column}')
                button.installEventFilter(self)
                self.buttons[(row, column)] = button
                internal_layout.addWidget(button, row, column)
        self.layout.addLayout(internal_layout, 2, 0)

        self.setLayout(self.layout)

    def randomize_field(self):
        self.field = Field.randomize()
        for button in self.buttons.values():
            button.setText('')

        for ship in self.field.ships:
            for row, col in ship.coordinates:
                self.buttons[(row, col)].setText(str(ship.length))

    def rotate_ship(self, ship):
        old_coordinates = ship.coordinates
        try:
            new_coordinates = self.field.rotate_ship(ship)
        except ValueError:
            return

        for _row, _col in old_coordinates:
            if (_row, _col) not in new_coordinates:
                self.buttons[_row, _col].setText('')

        for _row, _col in new_coordinates:
            self.buttons[_row, _col].setText(str(ship.length))

    def place_ship(self, row, col):
        try:
            unplaced_ship: Ship = next(self.field.unplaced_ships())
        except StopIteration:
            return

        try:
            fields = self.field.place(unplaced_ship, row, col, Direction.horizontal)
        except ValueError:
            try:
                fields = self.field.place(unplaced_ship, row, col, Direction.vertical)
            except ValueError:
                return
        for _row, _col in fields:
            self.buttons[_row, _col].setText(str(unplaced_ship.length))

    def delete_ship(self, row, col):
        ship = self.field.covering_ship(row, col)
        if ship:
            old_coordinates = ship.coordinates
            for _row, _col in old_coordinates:
                self.buttons[_row, _col].setText('')
            ship.unplace()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            row, col = map(int, obj.objectName().split('_'))

            if event.button() == Qt.LeftButton:
                covering_ship: Ship = self.field.covering_ship(row, col)
                if covering_ship:
                    self.rotate_ship(covering_ship)
                else:
                    self.place_ship(row, col)

            elif event.button() == Qt.RightButton:
                self.delete_ship(row, col)

        return QObject.event(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = PlaceField()
    widget.resize(200, 200)
    widget.show()

    sys.exit(app.exec_())
