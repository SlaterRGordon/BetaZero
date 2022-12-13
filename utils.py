import numpy as np
import chess
import tensorflow as tf
from tensorflow import unique, reshape, cast
from keras.losses import categorical_crossentropy

piece_encoding = {
    1: {
        1: 0,  # white pawn
        2: 1,  # white rook
        3: 2,  # white knight
        4: 3,  # white bishop
        5: 4,  # white queen
        6: 5,  # white king
    },
    0: {
        1: 6,  # black pawn
        2: 7,  # black rook
        3: 8,  # black knight
        4: 9,  # black bishop
        5: 10, # black queen
        6: 11, # black king
    }
}

piece_decoding = {
    0: {'type': 1, 'color': 1},
    1: {'type': 2, 'color': 1},
    2: {'type': 3, 'color': 1},
    3: {'type': 4, 'color': 1},
    4: {'type': 5, 'color': 1}, 
    5: {'type': 6, 'color': 1},
    6: {'type': 1, 'color': 0},
    7: {'type': 2, 'color': 0},
    8: {'type': 3, 'color': 0},
    9: {'type': 4, 'color': 0},
    10: {'type': 5, 'color': 0},
    11: {'type': 6, 'color': 0},
}

resultConvert = {
    '1/2-1/2': 0,
    '1-0': 1,
    '0-1': -1
}

def stateEncoder(state):
    input = np.zeros((8, 8, 17))
    
    for rank in range(8):
        for file in range(8):
            square=chess.SQUARES[rank*8 + file]
            piece = state.piece_at(square)
            if piece is not None:
                color = 1 if piece.color == chess.Color else 0
                type = state.piece_type_at(square)
                input[rank][file][piece_encoding[color][type]] = 1
    
    # encode the active player (whose turn it is)        
    input[:, :, 12] = 1 if state.turn == True else 0
    
    # encode the castling rights of each player
    input[:, :, 13] = 1 if state.has_kingside_castling_rights(chess.WHITE) else 0
    input[:, :, 14] = 1 if state.has_queenside_castling_rights(chess.WHITE) else 0
    input[:, :, 15] = 1 if state.has_kingside_castling_rights(chess.BLACK) else 0
    input[:, :, 16] = 1 if state.has_queenside_castling_rights(chess.BLACK) else 0
    
    return np.expand_dims(input, axis=0)

def stateDecoder(state):
    # Create an empty chess board
    board = chess.Board()
    
    # Loop through each rank and file on the board
    for rank in range(8):
        for file in range(8):
            for i in range(12):
                # Get the encoded piece at the current rank and file
                encoded_piece = state[rank][file][i]
                if encoded_piece == 1:
                    board.set_piece_at(rank * 8 + file, chess.Piece(piece_decoding[i]['type'], piece_decoding[i]['color']))
                    
    board.turn = True if state[0, 0, 12] == 1 else False
    
    if state[0, 0, 13] == 1:
        board.castling_rights |= chess.BB_A1
    
    if state[0, 0, 14] == 1:
        board.castling_rights |= chess.BB_H1
        
    if state[0, 0, 15] == 1:
        board.castling_rights |= chess.BB_A8
        
    if state[0, 0, 16] == 1:
        board.castling_rights |= chess.BB_H8
                
    return board

def policyEncoder(policy, legal_moves):
    encodedPolicy = np.zeros(4096)
    for i, move in enumerate(legal_moves):
        encodedPolicy[(64 * move.from_square) + move.to_square] = policy[i]
        
    return encodedPolicy
  
def policyDecoder(policy, legal_moves):
    decodedPolicy = [0.0 for move in legal_moves]
    for i, move in enumerate(legal_moves):
        decodedPolicy[i] = policy[(64 * move.from_square) + move.to_square]
        
    return decodedPolicy

def softmax_cross_entropy_with_logits(y_true, y_pred):
	p = y_pred
	pi = y_true

	zero = tf.zeros(shape = tf.shape(pi), dtype=tf.float32)
	where = tf.equal(pi, zero)

	negatives = tf.fill(tf.shape(pi), -100.0) 
	p = tf.where(where, negatives, p)

	loss = tf.nn.softmax_cross_entropy_with_logits(labels = pi, logits = p)
 
	return loss
