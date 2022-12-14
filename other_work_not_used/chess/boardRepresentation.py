from .coordinate import Coordinate

class BoardRepresentation():
    files = "abcdefgh"
    ranks = "12345678"
    
    a1 = 0
    b1 = 1
    c1 = 2
    d1 = 3
    e1 = 4
    f1 = 5
    g1 = 6
    h1 = 7

    a8 = 56
    b8 = 57
    c8 = 58
    d8 = 59
    e8 = 60
    f8 = 61
    g8 = 62
    h8 = 63

    def getRank(self, square):
        return square >> 3
    
    def getFile(self, square):
        return square & 0b000111
    
    def getSquare(self, file, rank):
        return rank * 8 + file
    
    def getCoordinate(self, square):
        return Coordinate(self.getFile(square), self.getRank(square))
    
    def isLightSquare(self, file, rank):
        return (file + rank) % 2 != 0
    
    def squareNameCoordinate(self, file, rank):
        return self.files[file] + '' + self.ranks[rank]
    
    def squareName(self, square):
        return self.squareNameCoordinate(self.getCoordinate(square))
    
    def squareNameCoordinate(self, coordinate):
        #return coordinate.file + '' + coordinate.rank
        return self.files[coordinate.file] + '' + self.ranks[coordinate.rank]