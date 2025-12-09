class Position:
    """セルの位置を保持するクラス"""

    def __init__(self, row: int = 0, col: int = 0):
        self.row = max(row, 0)
        self.col = max(col, 0)

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        return False

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.row + other.row, self.col + other.col)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.row - other.row, self.col - other.col)
        return NotImplemented
