from keras.models import Sequential
from keras.layers import Dense, Activation, Reshape
from keras.optimizers import Adam
from keras import regularizers
import keras.backend as K
import numpy as np
import tensorflow as tf

class NeuralNetwork():
    """NeuralNetwork"""
    def __init__(self):
        self.model = self.createModel()

    def createModel(self):
        model = Sequential()
        """ Model takes in input vector of length 773
        Board is input of size 768 (64 squares *12 possible pieces)
        1 input for turn (Black/White)
        2 inputs for Black/White permanent castling rights
        1 input for en passant status
        1 input for en passant square (an int in range(64)) """
        model.add(Dense(1024,
            input_dim = 773,
            kernel_regularizer=regularizers.l2(0.01),
            activation='relu'))
        model.add(Dense(512,
            kernel_regularizer=regularizers.l2(0.01),
            activation='relu'))
        """ Output is size 4097
        First element - board evaluation
        Remaining vector of length 4096 - recommended action
        (softmax format so interpreted as probabilities)
        """

        def final_activation(output_layer):
            v = K.reshape(K.tanh(output_layer[:,0]), (-1,1))
            probs = K.softmax(output_layer[:,1:4096])
            return K.concatenate([v,probs])

        model.add(Dense(4097,
            kernel_regularizer=regularizers.l2(0.01),
            activation=final_activation))
            # note SHOULD BE TANH ACTIVATION ON BOARD EVALUATION


        def loss_function(yTrue,yPred):
            """ Loss function described in AlphaZero paper
            Note that regularization is built into the model
            z - actual outcome of game (in {0,-1,1})
            v - predicted board evaluation
            p - recommended action
            """
            z = yTrue[0]
            policy = yTrue[1:4096]
            v = yPred[0]
            p = yPred[1:4096]
            return (K.square(z-v) - K.dot(policy,K.log(p)))
        optimizer = Adam(lr=0.005)
        model.compile(loss=loss_function, optimizer=optimizer)
        return model


    # def train(self,examples):
    #
    # def predict(self,board):
    #
    # def save(self,filename):
    #
    # def load(self,filename):
