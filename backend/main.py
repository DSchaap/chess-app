from chessAI.Coach import Coach
from chessAI.Game import Game
from chessAI.NeuralNet import KerasManager as nnwraper

import random
import math

args = {
    'numIters': 4,
    'numEps': 10,
    'tempThreshold': 15,
    'updateThreshold': 0.55,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 25,
    'arenaCompare': 6,
    'cpuct': 1,
    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp/','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

}

if __name__=="__main__":
    g = Game()

    # nnet = nn(g)
    # pnet = nn(g)
    nmanager = nnwraper()
    nmanager.start()
    pmanager = nnwraper()
    pmanager.start()
    nnet = nmanager.NeuralNet(g)
    pnet = pmanager.NeuralNet(g)
    nnet.initialize_model()
    pnet.initialize_model()

    if args['load_model']:
        nnet.load_checkpoint(folder=args['load_folder_file'][0], filename='temp.pth.tar')

    c = Coach(g, nnet, pnet, args)
    if args['load_model']:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
