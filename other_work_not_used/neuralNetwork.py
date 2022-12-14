import numpy as np
import chess  
        
def convertState(state):
    colors = [chess.WHITE, chess.BLACK]
    pieces = [chess.KING, chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
    
    convertedState = []
    for color in colors:
        for piece in pieces:
            board = [0 for i in range(64)]
            occupied = list(state.pieces(piece, color))
            
            for square in occupied:
                board[square] = 1
                
            convertedState.append(board)
    
    if state.turn == colors[0]:
        convertedState.append([1 for i in range(64)])
    else:
        convertedState.append([0 for i in range(64)])
        
    if state.can_claim_draw():
        convertedState.append([1 for i in range(64)])
    else:
        convertedState.append([0 for i in range(64)])
        
    return np.array(convertedState)[..., np.newaxis]
        
def convertMove(move):
    convertedMove = [0 for i in range(64*64)]
    convertedMove[(64 * move.from_square) + move.to_square]
    
    return np.array(convertedMove)

def convertOutput(output):
    pass

# Neural Network
class NeuralNetwork():
    def __init__(self, layers, learningRate=0.2):
        self.layers = layers
        self.learningRate = learningRate
        self.count = 0

    def forwardPass(self, input, isTraining=False):
        input = np.array(input)
        for layer in self.layers:
            input = layer.forwardPass(input, self.count)
            
        if isTraining:
            self.count += 1
            
        return input

    def backwardPass(self, error):
        for layer in reversed(self.layers):
            error = layer.backwardPass(error, self.learningRate)

        return error
    
    def train(self, states, values, moves, mse=False):
        convertedStates = []
        convertedMoves = []
        predictions = []
        
        for i, state in enumerate(states):
            convertedState = convertState(state)
            convertedStates.append(np.array(convertedState))
            convertedMoves.append(convertMove(moves[i]))

        if mse:
            predictions = self.forwardPass(input=convertedStates, isTraining=True)
        else:
            predictions = self.forwardPass(input=convertedStates)
        
        if mse:
            error = MSE.gradient(predictions, np.array(values))
            self.backwardPass(error)
            loss = MSE.loss(predictions, np.array(values))
            accuracy = MSE.accuracy(np.argmax(predictions), np.argmax(values))
        else:
            error = CrossEntropy.gradient(predictions, np.array(convertedMoves))
            self.backwardPass(error)
            loss = CrossEntropy.loss(predictions, np.array(convertedMoves))
            accuracy = CrossEntropy.accuracy(np.argmax(predictions), np.argmax(convertedMoves))
            
        return loss, accuracy

# Layer of neurons
class Layer():
    def __init__(self, n_in, n_out, type):
        self.weights = self.weightInitialization(n_in, n_out)
        self.biases = np.zeros((1, n_out))
        self.type = type

    # xavier weight initialization
    def weightInitialization(self, n_in, n_out):
        bound = np.sqrt(2 / float(n_in + n_out))
        weights = -bound + np.random.normal(0.0, bound, (n_in, n_out))

        return weights

    def forwardPass(self, input, count):
        self.input = input
        self.output = np.dot(input, self.weights) + self.biases

        return self.output

    def backwardPass(self, error, learningRate):
        inputError = np.dot(error, self.weights.T)
        gradientLoss = np.dot(self.input.T, error)
        
        self.weights -=  gradientLoss * learningRate
        self.biases -= np.mean(error) * learningRate
        
        return inputError

class LeakyReLuActivationLayer():
    def forwardPass(self, input, count):
        self.input = input
        self.output = np.where(input > 0, input, 0.2 * input)
        
        return self.output

    def backwardPass(self, error, learningRate):
        return self.gradient(self.input) * error

    def gradient(self, output):
        gradient = np.where(output >= 0, 1, 0.2)

        return gradient

# Sigmoid Activation Layer
class SigmoidActivationLayer():
    def forwardPass(self, input, count):
        self.input = input
        self.output = 1 / (1 + np.exp(-input))

        return self.output

    def backwardPass(self, error, learningRate):
        return self.gradient(self.input) * error
    
    def gradient(self, output):
        gradient = np.exp(-output) / np.square(1 + np.exp(-output))

        return gradient
        
# TanH Activation Layer
class TanHActivationLayer():
    def forwardPass(self, input, count):
        postiveExp = np.exp(input)
        negativeExp = np.exp(-input)
        postiveExp[postiveExp == np.inf] = 1
        negativeExp[negativeExp == np.inf] = 1
    
        self.input = input
        self.output = (postiveExp - negativeExp) / (postiveExp + negativeExp)

        return self.output

    def backwardPass(self, error, learningRate):
        return self.gradient(self.input) * error
    
    def gradient(self, output):
        gradient = 1 - np.square(output)

        return gradient

# Softmax Activation Layer
class SoftMaxActivationLayer():
    def forwardPass(self, input, count):
        self.input = input
        exps = np.exp(input - np.max(input, axis=-1, keepdims=True))
        self.output = exps / np.sum(exps, axis=-1, keepdims=True)

        return self.output

    def backwardPass(self, error, learningRate):
        return self.gradient(self.input) * error

    def gradient(self, output):
        gradient = self.forwardPass(output, 0)

        return gradient * (1 - gradient)

# Binary Cross Entropy for Loss
class CrossEntropy():
    def loss(output, target):
        output = np.clip(output, 1e-15, 1 - 1e-15) # clip values to avoid infinite values
        return -(target * np.log(output) + (1 - target) * np.log(1 - output))
    
    def gradient(output, target):
        output = np.clip(output, 1e-15, 1 - 1e-15) # clip values to avoid infinite values
        return -(target / output) + (1 - target) / (1 - output)

    # Find percentage of correctly predicted outputs
    def accuracy(output, target):
        matches = np.sum(target.reshape(-1,1) == output, axis=0)

        return  matches / 1


class MSE():
    def loss(output, target):
        target = target.reshape(-1,1)
        squared_differences = np.square(np.subtract(target, output))
        return squared_differences.mean()

    def gradient(output, target):
        return 2*(output-target.reshape(-1,1))/np.shape(output)[1]

    # Find percentage of correctly predicted outputs
    def accuracy(output, target):
        matches = np.sum(target.reshape(-1,1) == output, axis=0)

        return  matches / 1