import random
import sys
from time import sleep

from PySide2.QtCore import QEvent, Qt, QObject
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QGridLayout, QLabel

from models import Field, Ship, Direction, ShotResult, NEAR_COORDINATES


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

        label = QLabel('Place your ships.')

        randomize_btn = QPushButton(text='randomize')
        randomize_btn.clicked.connect(self.randomize_field)

        internal_layout = QGridLayout()
        internal_layout.setSpacing(0)
        for row in range(10):
            for column in range(10):
                button = QPushButton()
                button.setFixedSize(20, 20)
                button.setObjectName(f'{row}_{column}')
                button.installEventFilter(self)
                self.buttons[(row, column)] = button
                internal_layout.addWidget(button, row, column)

        self.next_btn = QPushButton(text='Start')
        self.next_btn.clicked.connect(root_widget.start_battle)
        self.next_btn.setEnabled(False)

        main_layout.addWidget(label, 0, 0, Qt.AlignCenter)
        main_layout.addWidget(randomize_btn, 1, 0)
        main_layout.addLayout(internal_layout, 3, 0)
        main_layout.addWidget(self.next_btn, 5, 0)

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
        self.user_field = field
        self.ai_field = Field.randomize()
        self.user_buttons = {}
        self.ai_buttons = {}
        self.help_text = None
        self.lock = False
        self.init_visual()

    def init_visual(self):
        main_layout = QGridLayout()

        self.help_text = QLabel('Your turn')

        user_field_layout = QGridLayout()
        user_field_layout.setSpacing(0)
        self.init_user_field(user_field_layout)

        ai_field_layout = QGridLayout()
        ai_field_layout.setSpacing(0)
        self.init_ai_field(ai_field_layout)

        new_game_btn = QPushButton(text='New Game')
        new_game_btn.clicked.connect(root_widget.start_placement)

        main_layout.addWidget(self.help_text, 0, 0, 1, 2, Qt.AlignCenter)
        main_layout.addLayout(user_field_layout, 1, 0)
        main_layout.addLayout(ai_field_layout, 1, 1)
        main_layout.addWidget(new_game_btn, 3, 0, 1, 2, Qt.AlignCenter)
        self.setLayout(main_layout)

    def init_ai_field(self, layout):
        for row in range(10):
            for column in range(10):
                button = QPushButton()
                button.setFixedSize(20, 20)
                button.setObjectName(f'{row}_{column}')
                button.installEventFilter(self)
                self.ai_buttons[(row, column)] = button
                layout.addWidget(button, row, column)

    def init_user_field(self, layout):
        for row in range(10):
            for column in range(10):
                button = QPushButton()
                button.setFixedSize(20, 20)
                button.setEnabled(False)
                self.user_buttons[(row, column)] = button
                layout.addWidget(button, row, column)

        for ship in self.user_field.ships:
            for row, col in ship.coordinates:
                self.user_buttons[(row, col)].setText(str(ship.length))

    def shot(self, btn, row, col, user_turn):
        if user_turn:
            buttons = self.ai_buttons
            field = self.ai_field
        else:
            buttons = self.user_buttons
            field = self.user_field

        ship: Ship = field.covering_ship(row, col)

        if not ship:
            btn.setText('.')
            return ShotResult.miss

        btn.setText('x')
        ship.shot(row, col)

        if ship.alive:
            return ShotResult.hit

        for row, col in ship.coordinates:
            for x, y in NEAR_COORDINATES:
                coords = (row + x, col + y)
                if coords in buttons and not buttons[coords].text():
                    buttons[coords].setText('.')
                    buttons[coords].removeEventFilter(self)
        return ShotResult.kill

    def endgame(self, user_won=True):
        if user_won:
            self.help_text.setText('You win')
        else:
            self.help_text.setText('You lose')
        for button in self.ai_buttons.values():
            button.removeEventFilter(self)

    def ai_turns(self):
        possible_turns = list(filter(lambda x: x[1].text() not in ('.', 'x'), self.user_buttons.items()))
        random.shuffle(possible_turns)
        for coords, button in possible_turns:
            self.repaint()
            sleep(1)
            ai_shot = self.shot(button, *coords, user_turn=False)
            if ai_shot == ShotResult.hit:
                self.help_text.setText('Nice hit. AI shot again')
            elif ai_shot == ShotResult.kill:
                self.help_text.setText('You lose one ship. AI shot again')
                if self.user_field.empty:
                    self.endgame(user_won=False)
            else:
                self.help_text.setText('You are lucky. AI miss. Your turn')
                break

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and not self.lock:
            self.lock = True
            row, col = map(int, obj.objectName().split('_'))

            user_shot = self.shot(obj, row, col, user_turn=True)
            obj.removeEventFilter(self)

            if user_shot == ShotResult.hit:
                self.help_text.setText('Nice hit. Shot again')
            elif user_shot == ShotResult.kill:
                self.help_text.setText('You kill it. Shot again')
                if self.ai_field.empty:
                    self.endgame(user_won=True)
            else:
                self.help_text.setText('You miss. AI turn')
                self.ai_turns()

            self.lock = False
        return QObject.event(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    root_widget = RootWidget()
    root_widget.start_placement()
    root_widget.show()
    # root_widget.setFixedSize(root_widget.size())
    root_widget.setFixedSize(0, 0)

    sys.exit(app.exec_())
