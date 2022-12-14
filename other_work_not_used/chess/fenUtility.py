from .boardRepresentation import BoardRepresentation

import numpy as np

class PositionInfo():
    def __init__(self):
        self.squares = np.zeros(64)
        self.whiteCastleKingside = False
        self.whiteCastleQueenside = False
        self.blackCastleKingside = False
        self.blackCastleQueenside = False
        self.epFile = 0
        self.whiteToMove = True
        self.n_moves = 0
        self.playCount = 0

class FenUtility(PositionInfo):
    typeDictionary = {
        'k': 1,
        'p': 2,
        'n': 3,
        'b': 5,
        'r': 6,
        'q': 7
    }
    
    positionInfo = PositionInfo()
    
    def positionFromFen(self, fen):
        sections = str.split(fen, ' ')
        
        file = 0
        rank = 7
        
        for symbol in sections[0]:
            if symbol == '/':
                file = 0
                rank -= 1
            else:
                if symbol.isdigit():
                    file += int(symbol)
                else:
                    color = 8 if symbol.isupper() else 16
                    type = self.typeDictionary[str.lower(symbol)]
                    self.positionInfo.squares[rank * 8 + file] = type | color
                    file += 1
                    
        self.positionInfo.whiteToMove = (sections[1] == "w")
        
        castlingRights = sections[2] if (len(sections) > 2) else "KQkq"
        self.positionInfo.whiteCastleKingside = "K" in castlingRights
        self.positionInfo.whiteCastleQueenside = "Q" in castlingRights
        self.positionInfo.blackCastleKingside = "k" in castlingRights
        self.positionInfo.blackCastleQueenside = "q" in castlingRights
        
        if len(sections) > 3:
            enPassantFileName = str(sections[3][0])
            if enPassantFileName in BoardRepresentation().files:
                self.positionInfo.epFile = BoardRepresentation().files[enPassantFileName] + 1

        if len(sections) > 4:
            self.positionInfo.playCount = int(sections[4])
        
        return self.positionInfo
                
