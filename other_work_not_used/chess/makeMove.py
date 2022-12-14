from .pieceList import PieceList
from .piece import Piece
from .move import Move, Flag
from .boardRepresentation import BoardRepresentation

class MakeMove(Move):
    def __init__(self, move, board):
        self.board = board
        self.move = move
        
        self.whiteToMove = True if self.board.colorToMove == 8 else False
        
        self.whiteCastleKingsideMask = 0b1111111111111110
        self.whiteCastleQueensideMask = 0b1111111111111101
        self.blackCastleKingsideMask = 0b1111111111111011
        self.blackCastleQueensideMask = 0b1111111111110111

        self.whiteCastleMask = self.whiteCastleKingsideMask & self.whiteCastleQueensideMask
        self.blackCastleMask = self.blackCastleKingsideMask & self.blackCastleQueensideMask
        
        self.oldEnPassantFile = (self.board.currentGameState >> 4) & 15
        self.originalCastleState = self.board.currentGameState & 15
        self.newCastleState = self.originalCastleState

        self.opponentColorIndex = 1 - self.board.colorToMoveIndex
        self.moveFrom = move.getStartSquare()
        self.moveTo = move.getTargetSquare()
        self.capturedPieceType = Piece().type(self.board.squares[self.moveTo])
        self.movePiece = self.board.squares[self.moveFrom]
        self.movePieceType = Piece().type(self.movePiece)

        self.moveFlag = self.move.moveFlagValue()
        self.isPromotion = move.isPromotion()
        self.isEnPassant = self.moveFlag == Flag().enPassantCapture
        
        self.handleCaptures()
        
        self.movePieces()
        self.pieceOnTargetSquare = self.movePiece
        
        self.handlePromotion()
        self.board.squares[self.moveTo] = self.pieceOnTargetSquare
        self.board.squares[self.moveFrom] = 0
        
        self.handleCastleRights()
        
        self.board.zobristKey ^= self.board.zobrist.sideToMove
        self.board.zobristKey ^= self.board.zobrist.pieces[self.moveFrom][self.movePieceType][self.board.colorToMoveIndex]
        self.board.zobristKey ^= self.board.zobrist.pieces[self.moveTo][Piece().type(self.pieceOnTargetSquare)][self.board.colorToMoveIndex]
        
        if self.oldEnPassantFile != 0:
            self.board.zobristKey ^= self.board.zobrist.enPassantFile[self.oldEnPassantFile]
            
        if self.newCastleState != self.originalCastleState:
            self.board.zobristKey ^= int(self.board.zobrist.castlingRights[self.originalCastleState]) # remove old castling rights state
            self.board.zobristKey ^= int(self.board.zobrist.castlingRights[self.newCastleState])
            
        self.board.currentGameState |= self.newCastleState
        self.board.gameStateHistory.append(self.board.currentGameState)
        
        # Change side to move
        self.board.colorToMove = 8 if not self.whiteToMove else 16
        self.board.opponentColor = 16 if not self.whiteToMove else 8
        self.board.whiteToMove = not self.whiteToMove
        self.board.colorToMoveIndex = 1 - self.board.colorToMoveIndex
        self.board.playCount += 1
        
    def handleCaptures(self):
        self.board.currentGameState |= (self.capturedPieceType << 8)
        if self.capturedPieceType != 0 and not self.isEnPassant:
            self.board.zobristKey ^= self.board.zobrist.pieces[self.moveTo][self.capturedPieceType][self.opponentColorIndex]
            pieceList = self.board.getPieceList(self.capturedPieceType, self.opponentColorIndex)
            pieceList.removePiece(self.moveTo)
    
    def movePieces(self):
        if self.movePieceType == Piece().king:
            self.board.kingSquare[self.board.colorToMoveIndex] = self.moveTo
            self.newCastleState &= self.whiteCastleMask if self.whiteToMove else self.blackCastleMask
        else:
            self.board.getPieceList(self.movePieceType, self.board.colorToMoveIndex).movePiece(self.moveFrom, self.moveTo)
    
    def handlePromotion(self):
        if self.isPromotion:
            promoteType = 0
            if self.moveFlag == Flag().promoteToQueen:
                promoteType = Piece().queen
                self.board.getPieceList(promoteType, self.board.colorToMoveIndex).addPiece(self.moveTo)
            elif self.moveFlag == Flag().promoteToKnight:
                promoteType = Piece().knight
                self.board.getPieceList(promoteType, self.board.colorToMoveIndex).addPiece(self.moveTo)
            elif self.moveFlag == Flag().promoteToRook:
                promoteType = Piece().rook
                self.board.getPieceList(promoteType, self.board.colorToMoveIndex).addPiece(self.moveTo)
            elif self.moveFlag == Flag().promoteToBishop:
                promoteType = Piece().bishop
                self.board.getPieceList(promoteType, self.board.colorToMoveIndex).addPiece(self.moveTo)
                
            self.pieceOnTargetSquare = promoteType | self.board.colorToMove
            type = Piece().pawn
            self.board.getPieceList(type, self.board.colorToMoveIndex).removePiece(self.moveTo)
        else:
            if self.moveFlag == Flag().enPassantCapture:
                epPawnSquare = self.moveTo + -8 if (self.colorToMove == 8) else 8
                self.board.currentGameState |= self.board.squares[epPawnSquare] << 8 # add pawn as capture type
                self.board.squares[epPawnSquare] = 0 # clear ep capture square
                self.board.pawns[self.opponentColorIndex].removePiece(epPawnSquare)
                self.board.zobristKey ^= self.board.zobrist.pieces[epPawnSquare][Piece().pawn][self.opponentColorIndex]
            elif self.moveFlag == Flag().castling:
                kingside = self.moveTo == BoardRepresentation().g1 or self.moveTo == BoardRepresentation().g8
                castlingRookFromIndex = self.moveTo + 1 if kingside else self.moveTo - 2
                castlingRookToIndex = self.moveTo - 1 if kingside else self.moveTo + 1

                self.board.squares[castlingRookFromIndex] = Piece().none
                self.board.squares[castlingRookToIndex] = Piece().rook | self.colorToMove

                self.board.rooks[self.colorToMoveIndex].MovePiece (castlingRookFromIndex, castlingRookToIndex)
                ZobristKey ^= self.board.zobrist.pieces[castlingRookFromIndex][Piece().rook][self.board.colorToMoveIndex]
                ZobristKey ^= self.board.zobrist.pieces[castlingRookToIndex][Piece().rook][self.board.colorToMoveIndex]
    
    def handleCastleRights(self):
        if self.originalCastleState != 0:
            if self.moveTo == BoardRepresentation().h1 or self.moveFrom == BoardRepresentation().h1:
                self.newCastleState &= self.whiteCastleKingsideMask
            elif self.moveTo == BoardRepresentation().a1 or self.moveFrom == BoardRepresentation().a1:
                self.newCastleState &= self.whiteCastleQueensideMask
            elif self.moveTo == BoardRepresentation().h8 or self.moveFrom == BoardRepresentation().h8:
                self.newCastleState &= self.blackCastleKingsideMask
            elif self.moveTo == BoardRepresentation().a8 or self.moveFrom == BoardRepresentation().a8:
                self.newCastleState &= self.blackCastleQueensideMask
                
    def getBoard(self):
        return self.board