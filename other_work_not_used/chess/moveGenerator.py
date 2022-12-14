from .piece import Piece
from .precomputedData import PrecomputedData
from .move import Move, Flag
from .boardRepresentation import BoardRepresentation

class MoveGenerator():
    def __init__(self, board, includeQuietMoves = True):
        self.board = board
        self.directionOffsets = [8, -8, -1, 1, 7, -7, 9, -9]
        
        self.inCheck = False
        self.inDoubleCheck = False
        self.checkRayBitmask = 0
        self.pinRayBitmask = 0
        self.pinsExistInPosition = False
        
        self.opponentColorIndex = 1 - self.board.colorToMoveIndex
        
        self.opponentSlidingAttackMap = 0
        self.opponentAttackMap = None
        self.opponentAttackMapNoPawns = None
        self.friendlyKingSquare = int(self.board.kingSquare[self.board.colorToMoveIndex])
        
        self.moves = []
        
        self.genQuiets = includeQuietMoves
        
        self.piece = Piece()
        self.boardRepresentation = BoardRepresentation()
        self.preData = PrecomputedData()
        
        self.calculateAttackData()
        self.getKingMoves()
        
        # Only king moves are valid in a double check position, so can return early.
        if self.inDoubleCheck:
            return self.moves
   
        self.getSlidingMoves()
        self.getKnightMoves()
        self.getPawnMoves()
    
    def isPinned (self, square):
        return self.pinsExistInPosition and ((int(self.pinRayBitmask) >> int(square)) & 1) != 0
    
    def squareIsInCheckRay(self, square):
        return self.inCheck and ((int(self.checkRayBitmask) >> int(square)) & 1) != 0
    
    def isMovingAlongRay (self, rayDir, startSquare, targetSquare):
        moveDir = self.preData.directionLookup[targetSquare - startSquare + 63]
        return (rayDir == moveDir or -rayDir == moveDir)
    
    def hasKingsideCastleRight(self):
        mask = 1 if self.board.whiteToMove else 4
        return self.board.currentGameState & mask != 0
    
    def hasQueensideCastleRight(self):
        mask = 2 if self.board.whiteToMove else 8
        return self.board.currentGameState & mask != 0
    
    def getKingMoves(self):
        for i in range(len(self.preData.kingMoves[self.friendlyKingSquare])):
            targetSquare = self.preData.kingMoves[self.friendlyKingSquare][i]
            pieceOnTargetSquare = self.board.squares[targetSquare]
   
            # Skip squares occupied by friendly pieces
            if self.piece.isColor(pieceOnTargetSquare, self.board.colorToMove):
                continue
            
            isCapture = self.piece.isColor(pieceOnTargetSquare, self.board.opponentColor)
            if not isCapture:
                # King can't move to square marked as under enemy control, unless he is capturing that piece
                # Also skip if not generating quiet moves
                if not self.genQuiets or self.squareIsInCheckRay(targetSquare):
                    continue
                
            # Safe for king to move to this square
            if not self.containsSquare(self.opponentAttackMap, targetSquare):
                self.moves.append(Move().moveSquare(self.friendlyKingSquare, targetSquare))
                
                # Castling:
                if not self.inCheck and not isCapture:
                    # Castle kingside
                    if (targetSquare == self.boardRepresentation.f1 or targetSquare == self.boardRepresentation.f8) and self.hasKingsideCastleRight:
                        castleKingsideSquare = targetSquare + 1
                        if self.board.squares[castleKingsideSquare] == self.piece.none:
                            if not self.containsSquare(self.opponentAttackMap, castleKingsideSquare):
                                self.moves.append(Move().moveFlag(self.friendlyKingSquare, castleKingsideSquare, Flag().castling))
                    # Castle queenside
                    elif (targetSquare == self.boardRepresentation.d1 or targetSquare == self.boardRepresentation.d8) and self.hasQueensideCastleRight:
                        castleQueensideSquare = targetSquare - 1
                        if self.board.squares[castleQueensideSquare] == self.piece.none and self.board.squares[castleQueensideSquare - 1] == self.piece.none:
                            if not self.containsSquare(self.opponentAttackMap, castleQueensideSquare):
                                self.moves.append(Move().moveFlag(self.friendlyKingSquare, castleQueensideSquare, Flag().castling))
    
    def getSlidingMoves(self):
        rooks = self.board.getPieceList(self.piece.rook, self.board.colorToMoveIndex)
        bishops = self.board.getPieceList(self.piece.bishop, self.board.colorToMoveIndex)
        queens = self.board.getPieceList(self.piece.queen, self.board.colorToMoveIndex)
        
        for i in range(rooks.n_pieces):
            self.getSlidingPieceMoves(rooks.occupied[i], 0, 4)
            
        for i in range(bishops.n_pieces):
            self.getSlidingPieceMoves(bishops.occupied[i], 4, 8)
            
        for i in range(queens.n_pieces):
            self.getSlidingPieceMoves(queens.occupied[i], 0, 8)
            
    def getSlidingPieceMoves(self, startSquare, startDirectionIndex, endDirectionIndex):
        # If this piece is pinned, and the king is in check, this piece cannot move
        isPinned = self.isPinned(startSquare)
        if self.inCheck and isPinned:
            return
    
        for directionIndex in range(startDirectionIndex, endDirectionIndex):
            currentDirOffset = self.preData.directionOffsets[directionIndex]
            
            # If pinned, this piece can only move along the ray towards/away from the friendly king, so skip other directions
            if isPinned and not self.isMovingAlongRay(currentDirOffset, self.friendlyKingSquare, startSquare):
                continue
            
            for n in range(self.preData.numSquaresToEdge[startSquare][directionIndex]):
                targetSquare = startSquare + currentDirOffset * (n + 1)
                targetSquarePiece = self.board.squares[targetSquare]
                
                # Blocked by friendly piece, so stop looking in this direction
                if self.piece.isColor(targetSquarePiece, self.board.colorToMove):
                    break
                isCapture = targetSquarePiece != self.piece.none
                
                movePreventsCheck = self.squareIsInCheckRay(targetSquare)
                if movePreventsCheck or not self.inCheck:
                    if self.genQuiets or isCapture:
                        self.moves.append(Move().moveSquare(startSquare, targetSquare))
                        
                # If square not empty, can't move any further in this direction
                # Also, if this move blocked a check, further moves won't block the check
                if isCapture or movePreventsCheck:
                    break
    
    def getKnightMoves(self):
        knights = self.board.getPieceList(self.piece.knight, self.board.colorToMoveIndex)
        
        for i in range(knights.n_pieces):
            startSquare = knights.occupied[i]
            
            # Knight cannot move if it is pinned
            if self.isPinned(startSquare):
                continue
            
            for knightMoveIndex in range(len(self.preData.knightMoves[startSquare])):
                targetSquare = self.preData.knightMoves[startSquare][knightMoveIndex]
                targetSquarePiece = self.board.squares[targetSquare]
                isCapture = self.piece.isColor(targetSquarePiece, self.board.opponentColor)
                
                if self.genQuiets or isCapture:
                    # Skip if square contains friendly piece, or if in check and knight is not interposing/capturing checking piece
                    if self.piece.isColor(targetSquarePiece, self.board.colorToMove) or self.inCheck and not self.squareIsInCheckRay(targetSquare):
                        continue
                    
                    self.moves.append(Move().moveSquare(startSquare, targetSquare))
    
    def getPawnMoves(self):
        pawns = self.board.getPieceList(self.piece.pawn, self.board.colorToMoveIndex)
        
        pawnOffset = 8 if self.board.colorToMove == 8 else -8
        startRank = 1 if self.board.whiteToMove else 6
        finalRankBeforePromotion = 6 if self.board.whiteToMove else 1

        enPassantFile = (int(self.board.currentGameState >> 4) & 15) - 1
        enPassantSquare = -1
        if enPassantFile != -1:
            enPassantSquare = 8 * (5 if self.board.whiteToMove else 2) + enPassantFile
            
        for i in range(pawns.n_pieces):
            startSquare = pawns.occupied[i]
            rank = self.boardRepresentation.getRank(startSquare)
            oneStepFromPromotion = rank == finalRankBeforePromotion
            
            if self.genQuiets:
                squareOneForward = startSquare + pawnOffset
                
                # Square ahead of pawn is empty: forward moves
                if self.board.squares[squareOneForward] == self.piece.none:
                    # Pawn not pinned, or is moving along line of pin
                    if not self.isPinned(startSquare) or self.isMovingAlongRay(pawnOffset, startSquare, self.friendlyKingSquare):
                        # Not in check, or pawn is interposing checking piece
                        if not self.inCheck or self.squareIsInCheckRay(squareOneForward):
                            if oneStepFromPromotion:
                                self.makePromotionMoves(startSquare, squareOneForward)
                            else:
                                self.moves.append(Move().moveSquare(startSquare, squareOneForward))
                                
                        # Is on starting square (so can move two forward if not blocked)
                        if (rank == startRank):
                            squareTwoForward = squareOneForward + pawnOffset
                            if self.board.squares[squareTwoForward] == self.piece.none:
                                # Not in check, or pawn is interposing checking piece
                                if not self.inCheck or self.squareIsInCheckRay(squareTwoForward):
                                    self.moves.append(Move().moveFlag(startSquare, squareTwoForward, Flag().pawnTwoForward))
            
            # Pawn captures              
            for j in range(2):
                # Check if square exists diagonal to pawn
                if self.preData.numSquaresToEdge[startSquare][self.preData.pawnAttackDirections[self.board.colorToMoveIndex][j]] > 0:
                    # move in direction friendly pawns attack to get square from which enemy pawn would attack
                    pawnCaptureDir = self.preData.directionOffsets[self.preData.pawnAttackDirections[self.board.colorToMoveIndex][j]]
                    targetSquare = startSquare + pawnCaptureDir
                    targetPiece = self.board.squares[targetSquare]
                    
                    # If piece is pinned, and the square it wants to move to is not on same line as the pin, then skip this direction
                    if (self.isPinned(startSquare) and not self.isMovingAlongRay(pawnCaptureDir, self.friendlyKingSquare, startSquare)):
                        continue
                    
                    # Regular capture
                    if self.piece.isColor(targetPiece, self.board.opponentColor):
                        # If in check, and piece is not capturing/interposing the checking piece, then skip to next square
                        if self.inCheck and not self.squareIsInCheckRay(targetSquare):
                            continue
                        
                        if (oneStepFromPromotion):
                            self.makePromotionMoves(startSquare, targetSquare)
                        else:
                            self.moves.append(Move().moveSquare(startSquare, targetSquare))
                            
                        # Capture en-passant
                        if (targetSquare == enPassantSquare):
                            epCapturedPawnSquare = targetSquare + (-8 if self.board.whiteToMove else 8)
                            if not self.inCheckAfterEnPassant(startSquare, targetSquare, epCapturedPawnSquare):
                                self.moves.append(Move().moveFlag(startSquare, targetSquare, Flag().enPassantCapture))

    def inCheckAfterEnPassant(self, startSquare, targetSquare, epCapturedPawnSquare):
        # Update board to reflect en-passant capture
        self.board.squares[targetSquare] = self.board.squares[startSquare]
        self.board.squares[startSquare] = self.piece.none
        self.board.squares[epCapturedPawnSquare] = self.piece.none

        inCheckAfterEpCapture = False
        if self.squareAttackedAfterEPCapture(epCapturedPawnSquare, startSquare):
            inCheckAfterEpCapture = True

        # Undo change to board
        self.board.squares[targetSquare] = self.piece.none
        self.board.squares[startSquare] = self.piece.pawn | self.board.colorToMove
        self.board.squares[epCapturedPawnSquare] = self.piece.pawn | self.board.opponentColor
        return inCheckAfterEpCapture
    
    def makePromotionMoves(self, fromSquare, toSquare):
        self.moves.append(Move().moveFlag(fromSquare, toSquare, Flag().promoteToQueen))
        self.moves.append(Move().moveFlag(fromSquare, toSquare, Flag().promoteToKnight))
        self.moves.append(Move().moveFlag(fromSquare, toSquare, Flag().promoteToRook))
        self.moves.append(Move().moveFlag(fromSquare, toSquare, Flag().promoteToBishop))
    
    def calculateAttackData(self):
        self.genSlidingAttackMap()
        startDirectionIndex = 0
        endDirectionIndex = 8
        rooks = self.board.getPieceList(self.piece.rook, self.opponentColorIndex)
        bishops = self.board.getPieceList(self.piece.bishop, self.opponentColorIndex)
        queens = self.board.getPieceList(self.piece.queen, self.opponentColorIndex)
        
        if queens.n_pieces == 0:
            startDirectionIndex = 0 if rooks.n_pieces > 0 else 4
            endDirectionIndex = 8 if bishops.n_pieces > 0 else 4
  
        for directionIndex in range(startDirectionIndex, endDirectionIndex):
            isDiagonal = directionIndex > 3
            
            n = self.preData.numSquaresToEdge[self.friendlyKingSquare][directionIndex]
            directionOffset = self.directionOffsets[directionIndex]
            isFriendlyPieceAlongRay = False
            rayMask = 0
            
            for i in range(n):
                squareIndex = self.friendlyKingSquare + directionOffset * (i + 1)
                rayMask |= 1 << squareIndex
                piece = self.board.squares[squareIndex]
                
                # This square contains a piece
                if piece != self.piece.none:
                    if self.piece.isColor(piece, self.board.colorToMove):
                        if not isFriendlyPieceAlongRay:
                            isFriendlyPieceAlongRay = True
                        else:
                            break
                    else:
                        pieceType = self.piece.type(piece)
                        if isDiagonal and self.piece.isBishopOrQueen(pieceType) or not isDiagonal and self.piece.isRookOrQueen(pieceType):
                            if isFriendlyPieceAlongRay: # Friendly piece blocks the check, so this is a pin
                                self.pinsExistInPosition = True
                                self.pinRayBitmask |= rayMask
                            else: # No friendly piece blocking the attack, so this is a check
                                self.checkRayBitmask |= rayMask
                                self.inDoubleCheck = self.inCheck # if already in check, then this is double check
                                self.inCheck = True
                                
                            break
                
            if self.inDoubleCheck:
                break
        
        opponentKnights = self.board.getPieceList(self.piece.knight, self.opponentColorIndex)
        opponentKnightAttacks = 0
        isKnightCheck = False
        for knightIndex in range(opponentKnights.n_pieces):
            startSquare = opponentKnights.occupied[knightIndex]
            opponentKnightAttacks |= self.preData.knightAttackBitboards[startSquare]
            
            if not isKnightCheck and self.containsSquare(opponentKnightAttacks, self.friendlyKingSquare):
                isKnightCheck = True
                self.inDoubleCheck = self.inCheck # if already in check, then this is double check
                self.inCheck = True
                self.checkRayBitmask |= 1 << int(startSquare)
                
        opponentPawns = self.board.getPieceList(self.piece.pawn, self.opponentColorIndex) 
        opponentPawnAttacks = 0
        isPawnCheck = False
        for pawnIndex in range(opponentPawns.n_pieces):
            startSquare = opponentPawns.occupied[pawnIndex]
            pawnAttacks = self.preData.pawnAttackBitboards[startSquare][self.opponentColorIndex]
            opponentPawnAttacks |= pawnAttacks
            
            if not isPawnCheck and self.containsSquare(opponentPawnAttacks, self.friendlyKingSquare):
                isPawnCheck = True
                self.inDoubleCheck = self.inCheck # if already in check, then this is double check
                self.inCheck = True
                self.checkRayBitmask |= 1 << int(startSquare)
        enemyKingSquare = int(self.board.kingSquare[self.opponentColorIndex])
        self.opponentAttackMapNoPawns = int(self.opponentSlidingAttackMap) | int(opponentKnightAttacks) | int(self.preData.kingAttackBitboards[enemyKingSquare])
        self.opponentAttackMap = self.opponentAttackMapNoPawns | int(opponentPawnAttacks)
    
    def updateSlidingAttackPiece(self, startSquare, startDirectionIndex, endDirectionIndex):
        for directionIndex in range(startDirectionIndex, endDirectionIndex):
            currentDirOffset = self.directionOffsets[directionIndex]
            
            for n in range(self.preData.numSquaresToEdge[startSquare][directionIndex]):
                targetSquare = int(startSquare + currentDirOffset * (n + 1))
                targetSquarePiece = self.board.squares[targetSquare]
                self.opponentSlidingAttackMap |= 1 << targetSquare
                if (targetSquare != self.friendlyKingSquare):
                    if (targetSquarePiece != self.piece.none):
                        break
        
    def genSlidingAttackMap(self):
        self.opponentSlidingAttackMap = 0

        enemyRooks = self.board.getPieceList(self.piece.rook, self.opponentColorIndex) 
        for i in range(enemyRooks.n_pieces):
            self.updateSlidingAttackPiece(enemyRooks.occupied[i], 0, 4)
        
        enemyBishops = self.board.getPieceList(self.piece.bishop, self.opponentColorIndex) 
        for i in range(enemyBishops.n_pieces):
            self.updateSlidingAttackPiece(enemyBishops.occupied[i], 4, 8)
        
        enemyQueens = self.board.getPieceList(self.piece.queen, self.opponentColorIndex) 
        for i in range(enemyQueens.n_pieces):
            self.updateSlidingAttackPiece(enemyQueens.occupied[i], 0, 8)
            
    def containsSquare(self, bitboard, square):
        return ((int(bitboard) >> int(square)) & 1) != 0