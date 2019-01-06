from chessAI.Coach import Coach
from chessAI.Game import Game
from chessAI.NeuralNet import KerasManager
from multiprocessing import cpu_count
import random
import math

args = {
    'numIters': 4,
    'numEps': 10,
    'tempThreshold': 15,
    'updateThreshold': 0.55,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 15,
    'arenaCompare': 10,
    'cpuct': 1,
    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp/','temp.pth.tar'),
    'numItersForTrainExamplesHistory': 5,

}

if __name__=="__main__":
    g = Game()

    # nnet = nn(g)
    # pnet = nn(g)
    n_cpus = cpu_count()
    nmanagers = [KerasManager() for i in range(n_cpus)]
    [m.start() for m in nmanagers]
    pmanagers = [KerasManager() for i in range(n_cpus)]
    [m.start() for m in pmanagers]

    nnets = [m.NeuralNet(g) for m in nmanagers]
    [n.initialize_model() for n in nnets]
    pnets = [m.NeuralNet(g) for m in pmanagers]
    [n.initialize_model() for n in pnets]

    if args['load_model']:
        [n.load_checkpoint(folder=args['load_folder_file'][0], filename='temp.pth.tar') for n in nnets]

    c = Coach(g, nnets, pnets, args)
    if args['load_model']:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
