from nn import NeuralNetwork
from play import SelfPlay
from keras.optimizers import Adam
from keras.models import load_model
from utils import softmax_cross_entropy_with_logits
import os

# check if the best model exists
if os.path.exists('bestModel.h5'):
    model = load_model('bestModel.h5', custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits})
else:
    # create a new neural network
    nn = NeuralNetwork()
    model = nn.makeNeuralNetwork()
    model.compile(optimizer=Adam(learning_rate=0.01), loss=['mse', softmax_cross_entropy_with_logits])

# run simulations using the model
selfPlay = SelfPlay(model)
selfPlay.runSimulations()