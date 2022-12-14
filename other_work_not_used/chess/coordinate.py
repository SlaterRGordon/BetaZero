class Coordinate():
    def __init__(self, file, rank):
        self.file = file
        self.rank = rank
        
    def isLightSquare(self):
        return (self.file + self.rank) % 2 != 0
    
    def compareTo(self, coordinate):
        return 0 if (self.file == coordinate.file and self.rank == coordinate.rank) else 1