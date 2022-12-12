from nn import NeuralNetwork
from play import SelfPlay
from keras.optimizers import Adam
from keras.models import load_model
from utils import softmax_cross_entropy_with_logits
import os

if os.path.exists('bestModel.h5'):
    print('loading model')
    model = load_model('bestModel.h5', custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits})
    model.compile(optimizer=Adam(learning_rate=0.01), loss=['mse', softmax_cross_entropy_with_logits])
else:
    nn = NeuralNetwork()
    model = nn.makeNeuralNetwork()
    model.compile(optimizer=Adam(learning_rate=0.01), loss=['mse', softmax_cross_entropy_with_logits])

selfPlay = SelfPlay(model)
data = selfPlay.runSimulations()
print(data)