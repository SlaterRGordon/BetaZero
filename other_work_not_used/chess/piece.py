class Piece():
    none, king, pawn, knight, bishop, rook, queen = 0, 1, 2, 3, 5, 6, 7
    typeMask = 0b00111
    colorMask = 0b10000 | 0b01000

    def isColor(self, piece, color):
        return (int(piece) & self.colorMask) == color
    
    def color(self, piece):
        return int(piece) & self.colorMask

    def type(self, piece):
        return int(piece) & self.typeMask

    def isRookOrQueen(self, piece):
        return (int(piece) & 0b110) == 0b110

    def isBishopOrQueen(self, piece):
        return (int(piece) & 0b101) == 0b101

    def isSlidingPiece(self, piece):
        return (int(piece) & 0b100) != 0
