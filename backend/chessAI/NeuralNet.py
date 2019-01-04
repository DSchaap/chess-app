from keras.models import Model
from keras.layers import Dense, Activation, Reshape, BatchNormalization, Input, add
from keras.optimizers import Adam
from keras.losses import mean_squared_error, categorical_crossentropy
from keras import regularizers
import keras.backend as K
import numpy as np
import os
from multiprocessing.managers import BaseManager
import tensorflow as tf

class NeuralNet():
    """
    This class specifies the base NeuralNet class. To define your own neural
    network, subclass this class and implement the functions below. The neural
    network does not consider the current player, and instead only deals with
    the canonical form of the board.
    """

    def __init__(self,game):
        self.nnet = None
        self.graph = None
        self.action_size = game.getActionSize()

    def denseLayer(self,y,name,input_dim,output_dim):
        y = Dense(output_dim, input_dim = input_dim, name = 'dense_layer_' + name)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        return y

    def residualBlock(self,y,name, input_dim):
        shortcut = y
        y = Dense(input_dim, name = 'residual_layer_' + name)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)

        y = Dense(input_dim, name = 'residual_layer_2' + name)(y)
        y = BatchNormalization()(y)

        y = add([shortcut, y])
        y = Activation('relu')(y)
        return y

    def residual_network(self,X):
        """ Model takes in input vector of length 773
        Board is input of size 772 (64 squares *12 possible pieces)
        1 input for turn (Black/White)
        2 inputs for Black/White permanent castling rights
        1 input for en passant status
        1 input for en passant square (an int in range(64)) """

        """ Output is size 4097
        First element - board evaluation
        Remaining vector of length 4096 - recommended action
        (softmax format so interpreted as probabilities)
        """

        def final_activation(output_layer):
            v = K.reshape(K.tanh(output_layer[:,0]), (-1,1))
            probs = K.softmax(output_layer[:,1:4097])
            return K.concatenate([v,probs])


        y = self.denseLayer(X,'a',772,256)
        y = self.residualBlock(y,'b',256)
        y = self.denseLayer(y,'c',256,128)
        y = self.residualBlock(y,'d',128)
        y = self.residualBlock(y,'e',128)
        y = self.residualBlock(y,'f',128)
        y = self.residualBlock(y,'g',128)
        pred = Dense(4097, name = 'dense_out',activation=final_activation)(y)
        return pred

    def initialize_model(self):
        def loss_function(yTrue,yPred):
            """ Loss function described in AlphaZero paper
            Note that regularization is built into the model
            z - actual outcome of game (in {0,-1,1})
            v - predicted board evaluation
            p - vector of probabilities of actions
            """
            z = yTrue[:,0]
            policy = yTrue[:,1:4097]
            v = yPred[:,0]
            p = yPred[:,1:4097]
            return mean_squared_error(z,v)+categorical_crossentropy(policy,p)

        image_tensor = Input(shape=(772,), name = 'input_layer')
        network_output = self.residual_network(image_tensor)

        optimizer = Adam(lr=0.00001)
        model = Model(inputs=[image_tensor], outputs=[network_output])
        model.compile(loss=loss_function, optimizer=optimizer)
        model._make_predict_function()
        self.nnet = model
        self.graph = tf.get_default_graph()

    def train(self, examples,n_epochs=1):
        """
        This function trains the neural network with examples obtained from
        self-play.
        Input:
            examples: a list of training examples, where each example is of form
                      (board, pi, v). pi is the MCTS informed policy vector for
                      the given board, and v is its value. The examples has
                      board in its canonical form.
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = (np.asarray(input_boards))
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs).reshape((len(target_vs),1))
        target_y = (np.concatenate((target_vs,target_pis),axis=1))
        self.nnet.fit(x = input_boards, y = target_y, batch_size = 64, epochs = n_epochs)

    def predict(self, board):
        """
        Input:
            board: current board in its canonical form.
        Returns:
            pi: a policy vector for the current board- a numpy array of length
                game.getActionSize
            z: a float in [-1,1] that gives the value of the current board
        """
        board = np.array(board).reshape(1,772)
        with self.graph.as_default():
            v = self.nnet.predict(board)
        z = v[0][0]
        pi = v[0][1:4097]
        return pi,z

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path {}".format(filepath))
        self.nnet.load_weights(filepath)


class KerasManager(BaseManager):
    pass


KerasManager.register('NeuralNet', NeuralNet)
