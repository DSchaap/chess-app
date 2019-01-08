import numpy as np

class Move(object):
    """docstring for Move."""
    def __init__(self,piece,square):
        self.piece = piece
        self.newSquare = square

    def one_hot(self):
        """ There will be a one hot vector used to represent
        all possible moves. It will be 4096x1 with the first
        64 entries corresponding to all the possible squares to
        move to from square (0,0) and the next 64 all the
        possible squares to move to from square (0,1) and so on.
        This function puts a 1 in the coordinate corresponding
        to moving the piece provided to the square provided. """
        outVec = np.zeros((4096,))
        (newRow,newCol) = self.newSquare
        (oldRow,oldCol) = self.piece.position
        ind = 64*(oldRow*8+oldCol) + (newRow*8+newCol)
        outVec[int(ind)] = 1
        return outVec


def one_hot_to_move(onehot,board,player_color,inCanonicalForm):
    """ The following function returns the corresponding move
    from the one hot representation given the current board
    state. """
    board = board.board
    ind = onehot.argmax()
    newCol = ind%8
    newRow = (ind%64-newCol)/8
    oldCol = ((ind - (newRow*8+newCol))/64)%8
    oldRow = (((ind - (newRow*8+newCol))/64)-oldCol)/8
    if (player_color == -1 and inCanonicalForm):
        oldRow = -oldRow + 7
        newRow = -newRow + 7
    piece = board[(oldRow,oldCol)]
    return piece,(newRow,newCol)
