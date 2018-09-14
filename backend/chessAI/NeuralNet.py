from keras.models import Sequential
from keras.layers import Dense, Activation, Reshape
from keras.optimizers import Adam
from keras.losses import mean_squared_error, categorical_crossentropy
from keras import regularizers
import keras.backend as K
import numpy as np
import os

class NeuralNet():
    """
    This class specifies the base NeuralNet class. To define your own neural
    network, subclass this class and implement the functions below. The neural
    network does not consider the current player, and instead only deals with
    the canonical form of the board.
    See othello/NNet.py for an example implementation.
    """

    def __init__(self,game):
        self.nnet = self.createModel()
        self.action_size = game.getActionSize()

    def createModel(self):
        model = Sequential()
        """ Model takes in input vector of length 773
        Board is input of size 768 (64 squares *12 possible pieces)
        1 input for turn (Black/White)
        2 inputs for Black/White permanent castling rights
        1 input for en passant status
        1 input for en passant square (an int in range(64)) """
        model.add(Dense(1024,
            input_dim = 772,
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
            probs = K.softmax(output_layer[:,1:4097])
            return K.concatenate([v,probs])

        model.add(Dense(4097,
            kernel_regularizer=regularizers.l2(0.01),
            activation=final_activation))


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
        optimizer = Adam(lr=0.005)
        model.compile(loss=loss_function, optimizer=optimizer)
        return model

    def train(self, examples):
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
        self.nnet.fit(x = input_boards, y = target_y, batch_size = 64, epochs = 25)

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
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path {}".format(filepath))
        self.nnet.model.load_weights(filepath)
