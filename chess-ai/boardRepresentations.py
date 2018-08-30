import numpy as np


def pieceToOneHot(piece):
    oneHotPiece = { "WhitePawn": [1,0,0,0,0,0,0,0,0,0,0,0]
    , "WhiteKnight":[0,1,0,0,0,0,0,0,0,0,0,0]
    , "WhiteBishop":[0,0,1,0,0,0,0,0,0,0,0,0]
    , "WhiteRook":[0,0,0,1,0,0,0,0,0,0,0,0]
    , "WhiteQueen":[0,0,0,0,1,0,0,0,0,0,0,0]
    , "WhiteKing":[0,0,0,0,0,0,1,0,0,0,0,0]
    , "BlackPawn": [0,0,0,0,0,0,1,0,0,0,0,0]
    , "BlackKnight":[0,0,0,0,0,0,0,1,0,0,0,0]
    , "BlackBishop":[0,0,0,0,0,0,0,0,1,0,0,0]
    , "BlackRook":[0,0,0,0,0,0,0,0,0,1,0,0]
    , "BlackQueen":[0,0,0,0,0,0,0,0,0,0,1,0]
    , "BlackKing":[0,0,0,0,0,0,0,0,0,0,0,1]
    }
    outVec = oneHotPiece[piece["color"]+piece["denomination"]]
    return outVec

# Outputs a one hot representation of a given board
def boardToOneHot(board):
    outVec = []
    for i in range(8):
        for j in range(8):
            if [i,j] in board.keys():
                outVec = outVec + pieceToOneHot(board[(i,j)])
            else:
                outVec = outVec + [0,0,0,0,0,0,0,0,0,0,0,0]
    return outVec


def moveToOneHot(piece,newCoordinates):

    ''' There will be a one hot vector used to represent
    all possible moves. It will be 4096x1 with the first
    64 entries corresponding to all the possible squares to
    move to from square (0,0) and the next 64 all the
    possible squares to move to from square (0,1) and so on.
    This function puts a 1 in the coordinate corresponding
    to moving the piece provided to the square provided. '''


    outVec = np.zeros((4096,1))
    [newRow,newCol] = newCoordinates
    [oldRow,oldCol] = piece["position"]
    outVec[64*((oldRow)*8+(oldCol)) + ((newRow)*8+(newCol))] = 1
    return outVec



def oneHotToMove(onehot,board):

    ''' The following function returns the corresponding move
    from the one hot representation given the current board
    state. '''

    move = {}
    ind = onehot.argmax()
    newCol = ind%8
    newRow = (ind%64-6)/8
    oldCol = ((ind - ((newRow)*8+(newCol)))/64)%8
    oldRow = ((ind - ((newRow)*8+(newCol)))/64)-8*oldCol
    piece = board[(oldRow,oldCol)]
    move["piece"] = piece
    move["newPosition"] = [newRow,newCol]
    return move

def validMovesVec(model,legalMoves):

    '''Creates a one hot vector of legal moves'''

    outVec = np.zeros((4096,1))
    for move in legalMoves:
        outVec = outVec + moveToOneHot(move["piece"],move["newPosition"])
    return outVec
