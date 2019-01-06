import math
import numpy as np
from multiprocessing import Pool, Manager, cpu_count
import functools
EPS = 1e-8
manager = Manager()
class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnets, args):
        manager = Manager()
        self.game = game
        self.nnets = nnets
        self.net_ind = manager.dict()
        self.net_ind['ind'] = 0
        self.args = args
        self.Qsa = manager.dict()       # stores Q values for s,a (as defined in the paper)
        self.Nsa = manager.dict()       # stores #times edge s,a was visited
        self.Ns = manager.dict()        # stores #times board s was visited
        self.Ps = manager.dict()        # stores initial policy (returned by neural net)

        # self.Es = {}        # stores game.getGameEnded ended for board s
        # self.Vs = {}        # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.
        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        # now you share the model and graph between processes
        # in each process you can call this:
        with Pool(processes = cpu_count()) as p:
            scores = [p.apply_async(self.search, (canonicalBoard,)) for i in range(self.args['numMCTSSims'])]
            [s.get() for s in scores]

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa.get((s,a),0) for a in range(self.game.getActionSize())]

        if temp==0:
            bestA = np.argmax(counts)
            probs = [0]*len(counts)
            probs[bestA]=1
            return probs

        counts = [x**(1./temp) for x in counts]
        probs = [x/float(sum(counts)) for x in counts]
        return probs

    def search(self, canonicalBoard,recursionDepth=0):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.
        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.
        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.
        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        recursionDepth += 1
        s = self.game.stringRepresentation(canonicalBoard)

        Es = self.game.getGameEnded(canonicalBoard, 1)
        if Es!=0:
            return -Es

        if s not in self.Ps:
            # leaf node
            prev_net_ind = self.net_ind['ind']
            self.net_ind['ind'] = (self.net_ind['ind'] + 1) % 4
            self.Ps[s], v = self.nnets[prev_net_ind].predict(self.game.one_hot(canonicalBoard))
            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.Ps[s] = np.multiply(self.Ps[s],valids)     # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s    # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, do workaround.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Ns[s] = 0
            return -v

        valids = self.game.getValidMoves(canonicalBoard, 1)
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s,a) in self.Qsa:
                    u = self.Qsa.get((s,a),0) + self.args['cpuct']*self.Ps.get(s,[0]*4096)[a]*math.sqrt(self.Ns.get(s,0))/(1+self.Nsa.get((s,a),0))
                else:
                    u = self.args['cpuct']*self.Ps.get(s,[0]*4096)[a]*math.sqrt(self.Ns.get(s,0) + EPS)     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        onehot_a = np.zeros((4096,))
        onehot_a[a] = 1
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, onehot_a)
        next_s = self.game.getCanonicalForm(next_s, next_player)

        if (recursionDepth<900):
            v = self.search(next_s,recursionDepth)
        else:
            v = 1e-12

        self.Qsa[(s,a)] = (self.Nsa.get((s,a),0)*self.Qsa.get((s,a),0) + v)/(self.Nsa.get((s,a),0)+1)
        self.Nsa[(s,a)] = self.Nsa.get((s,a),0) + 1

        self.Ns[s] = self.Ns.get(s,0) + 1
        return -v
