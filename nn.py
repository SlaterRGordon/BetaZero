from keras.models import Model
from keras.layers import Input, Conv2D, Flatten, Dense, Conv3D, BatchNormalization, Activation, Add

class NeuralNetwork():
    def __init__(self):
        self.learningRate = 0.02
        
    def makeNeuralNetwork(self):
        input = Input(shape=(8, 8, 17))
        model = self.makeConvBlock(input)
        
        for i in range(1):
            model = self.makeResidualBlock(model)
            
        policyHead = self.makePolicyHead(model)
        valueHead = self.makeValueHead(model)
        
        model = Model(inputs=[input], outputs=[valueHead, policyHead])
        
        return model

    def makeConvBlock(self, model):
        model = Conv2D(filters=256, kernel_size=3, strides=1, padding='same')(model)
        model = BatchNormalization()(model)
        model = Activation('relu')(model)
        
        return model
        
    def makeResidualBlock(self, model):
        input = model
        model = Conv2D(filters=256, kernel_size=3, strides=1, padding='same')(model)
        model = BatchNormalization()(model)
        model = Activation('relu')(model)
        model = Conv2D(filters=256, kernel_size=3, strides=1, padding='same')(model)
        model = BatchNormalization()(model)
        model = Add()([model, input])
        model = Activation('relu')(model)
        
        return model
    
    def makePolicyHead(self, model):
        model = Conv2D(filters=2, kernel_size=1, strides=1, padding='same')(model)
        model = BatchNormalization()(model)
        model = Activation('relu')(model)
        model = Flatten()(model)
        model = Dense(units=4096, activation="softmax", name="policy")(model)
        
        return model
    
    def makeValueHead(self, model):
        model = Conv2D(filters=1, kernel_size=1, strides=1, padding='same')(model)
        model = BatchNormalization()(model)
        model = Activation('relu')(model)
        model = Flatten()(model)
        model = Dense(units=256)(model)
        model = Activation('relu')(model)
        model = Dense(units=1, activation="tanh", name="value")(model)
        
        return model
        