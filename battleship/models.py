import random
from enum import Enum

SHIP_LENGTHS = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)

NEAR_COORDINATES = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 0), (0, 1),
    (1, -1), (1, 0), (1, 1)
]


class ShotResult(Enum):
    miss = 'm'
    kill = 'k'
    hit = 'h'


class CellState:
    dead = False
    alive = True


class Direction(Enum):
    horizontal = 'h'
    vertical = 'v'


class Ship:
    row = None
    col = None
    direction: Direction = None
    _cells = []

    @classmethod
    def generate_ships(cls):
        return [cls(length) for length in SHIP_LENGTHS]

    def __init__(self, length):
        self._cells = [CellState.alive for _ in range(length)]

    @property
    def length(self):
        return len(self._cells)

    @property
    def dead(self):
        return all(cell == CellState.dead for cell in self._cells)

    @property
    def alive(self):
        return not self.dead

    @property
    def placed(self):
        return self.row is not None

    def includes(self, row, col):
        return (row, col) in self.coordinates

    def _get_cell(self, row, col):
        if not self.includes(row, col):
            return None

        if self.direction == Direction.horizontal:
            return col - self.col
        else:
            return row - self.row

    def shot(self, row, col):
        cell = self._get_cell(row, col)
        self._cells[cell] = CellState.dead

    @property
    def coordinates(self):
        if self.direction == Direction.vertical:
            return list(zip(range(self.row, self.row + self.length), (self.col for _ in range(self.length))))
        return list(zip((self.row for _ in range(self.length)), range(self.col, self.col + self.length)))

    def place(self, row, col, direction):
        if direction == Direction.horizontal and col + self.length > 10:
            raise ValueError
        if direction == Direction.vertical and row + self.length > 10:
            raise ValueError
        self.row = row
        self.col = col
        self.direction = direction

        return self.coordinates

    def unplace(self):
        self.row = None
        self.col = None


class Field:
    def __init__(self):
        self.ships = Ship.generate_ships()

    def unplaced_ships(self):
        while True:
            unplaced_ships = filter(lambda x: not x.placed, self.ships)
            sorted_ships = sorted(unplaced_ships, key=lambda x: x.length)
            if len(sorted_ships):
                yield sorted_ships[-1]
            else:
                break

    @property
    def empty(self):
        return all(
            ship.dead
            for ship in self.ships
        )

    def shot(self, row, col):
        for ship in self.ships:
            if ship.includes(row, col):
                ship.shot(row, col)
                return ShotResult.kill if ship.dead else ShotResult.hit

        return ShotResult.miss

    def place(self, ship: Ship, row, col, direction):
        ship.place(row, col, direction)

        searching_coordinates = []

        for row, col in ship.coordinates:
            for x, y in NEAR_COORDINATES:
                searching_coordinates.append((row + x, col + y))

        for _ship in self.ships:
            if not _ship.placed or _ship == ship:
                continue

            for row, col in searching_coordinates:
                if _ship.includes(row, col):
                    ship.unplace()
                    raise ValueError

        return ship.coordinates

    def covering_ship(self, row, col):
        for ship in self.ships:
            if ship.placed and ship.includes(row, col):
                return ship

    def rotate_ship(self, ship):
        return self.place(
            ship,
            row=ship.row,
            col=ship.col,
            direction=Direction.horizontal if ship.direction == Direction.vertical else Direction.vertical
        )

    @classmethod
    def randomize(cls):
        field = Field()
        for ship in field.unplaced_ships():
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            direction = random.choice((Direction.vertical, Direction.horizontal))
            try:
                field.place(ship, row, col, direction)
            except ValueError:
                continue
        return field
