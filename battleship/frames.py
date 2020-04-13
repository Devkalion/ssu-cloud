import sys

from PySide2.QtCore import QEvent, Qt, QObject
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QGridLayout, QLabel

from models import Field, Ship, Direction


class RootWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.placeField = None
        self.battleField = None

    def start_placement(self):
        if self.battleField:
            self.battleField.close()
        self.placeField = PlaceField()
        self.layout.addWidget(self.placeField)

    def start_battle(self):
        field = self.placeField.field
        self.placeField.close()
        self.battleField = BattleField(field)
        self.layout.addWidget(self.battleField)


class PlaceField(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = Field()
        self.buttons = {}
        self.next_btn = None

        self.init_visual()

    def init_visual(self):
        main_layout = QGridLayout()
        internal_layout = QGridLayout()
        internal_layout.setSpacing(0)

        label = QLabel('Place your ships.')
        main_layout.addWidget(label, 0, 0, Qt.AlignCenter)

        randomize_btn = QPushButton(text='randomize')
        randomize_btn.clicked.connect(self.randomize_field)
        main_layout.addWidget(randomize_btn, 1, 0)

        for row in range(10):
            for column in range(10):
                button = QPushButton()
                button.setFixedSize(20, 20)
                button.setObjectName(f'{row}_{column}')
                button.installEventFilter(self)
                self.buttons[(row, column)] = button
                internal_layout.addWidget(button, row, column)
        main_layout.addLayout(internal_layout, 3, 0)

        self.next_btn = QPushButton(text='Start')
        # TODO change for real action
        self.next_btn.clicked.connect(root_widget.start_battle)
        main_layout.addWidget(self.next_btn, 5, 0)
        self.next_btn.setEnabled(False)

        self.setLayout(main_layout)

    def randomize_field(self):
        self.field = Field.randomize()
        for button in self.buttons.values():
            button.setText('')

        for ship in self.field.ships:
            for row, col in ship.coordinates:
                self.buttons[(row, col)].setText(str(ship.length))

        self.next_btn.setEnabled(True)

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

        try:
            next(self.field.unplaced_ships())
        except StopIteration:
            self.next_btn.setEnabled(True)

    def delete_ship(self, ship):
        old_coordinates = ship.coordinates
        for _row, _col in old_coordinates:
            self.buttons[_row, _col].setText('')
        ship.unplace()
        self.next_btn.setEnabled(False)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            row, col = map(int, obj.objectName().split('_'))
            covering_ship: Ship = self.field.covering_ship(row, col)

            if event.button() == Qt.LeftButton:
                if covering_ship:
                    self.rotate_ship(covering_ship)
                else:
                    self.place_ship(row, col)

            elif event.button() == Qt.RightButton and covering_ship:
                self.delete_ship(covering_ship)

        return QObject.event(obj, event)


class BattleField(QWidget):
    def __init__(self, field, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout()
        self.field = field
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    root_widget = RootWidget()
    root_widget.start_placement()
    root_widget.show()
    # root_widget.setFixedSize(root_widget.size())

    sys.exit(app.exec_())
