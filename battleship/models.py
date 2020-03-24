from enum import Enum

SHIP_LENGTHS = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)


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
        return any(cell == CellState.alive for cell in self._cells)

    @property
    def alive(self):
        return not self.dead

    @property
    def placed(self):
        return self.row is not None

    def includes(self, row, col):
        return self._get_cell(row, col) is not None

    def _get_cell(self, row, col):
        if self.direction == Direction.horizontal:
            cell = col - self.col
        else:
            cell = row - self.row
        if 0 <= cell < self.length:
            return cell

    def shot(self, row, col):
        cell = self._get_cell(row, col)
        self._cells[cell] = CellState.dead

    def place(self, row, col, direction):
        if direction == Direction.horizontal and col + self.length > 10:
            raise ValueError
        if direction == Direction.vertical and row + self.length > 10:
            raise ValueError
        self.row = row
        self.col = col
        self.direction = direction

    def rotate(self):
        new_dir = Direction.horizontal if self.direction == Direction.vertical else Direction.vertical
        self.place(self.row, self.col, new_dir)


class Field:
    def __init__(self):
        self.ships = Ship.generate_ships()

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
