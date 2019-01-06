import asyncio
import websockets
import json
import numpy as np
from chessAI.Piece import Piece
from chessAI.Board import Board
from chessAI.Game import Game
from chessAI.NeuralNet import NeuralNet as nn
from chessAI.Move import one_hot_to_move
from chessAI.MCTS import MCTS

args = {
    'maxlenOfQueue': 200000,
    'numMCTSSims': 15,
    'cpuct': 1,
    'checkpoint': './temp/',
    'numItersForTrainExamplesHistory': 5,
}

g = Game()
nnet = nn(g)
nnet.initialize_model()
nnet.load_checkpoint(folder=args['checkpoint'], filename='temp.pth.tar')
mcts = MCTS(g, [nnet], args)


def decodeBoard(boardJSON):
    board = {}
    encodedBoard = json.loads(boardJSON)
    for key in encodedBoard["board"].keys():
        piece = encodedBoard["board"][key]
        board[eval(key)] = Piece(piece["denomination"],piece["color"],tuple(piece["position"]))
    board["whiteCastlingRights"] = tuple(encodedBoard["whiteCastlingRights"])
    board["blackCastlingRights"] = tuple(encodedBoard["blackCastlingRights"])
    board["whiteKing"] = tuple(encodedBoard["whiteKing"])
    board["blackKing"] = tuple(encodedBoard["blackKing"])
    if encodedBoard["enPassant"] == None:
        board["enPassant"] = encodedBoard["enPassant"]
    else:
        board["enPassant"] = tuple(encodedBoard["enPassant"])
    board["turn"] = encodedBoard["turn"]
    board["recentMoves"] = [(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]
    return board

def decideMove(game,board,curPlayer):
    canonicalBoard = game.getCanonicalForm(board, curPlayer)
    pi = mcts.getActionProb(canonicalBoard, temp=0,multiprocess=False)
    action = np.random.choice(len(pi), p=pi)
    onehot_action = np.zeros((4096,))
    onehot_action[action] = 1
    piece,(newRow,newCol) = one_hot_to_move(onehot_action,board,curPlayer)
    return {"piece":{"denomination":piece.denomination,"color":piece.color,"position":piece.position}, "newPosition":[int(newRow),int(newCol)]}


async def sendMove(websocket, path):
    boardJSON = await websocket.recv()
    print("< received board state")
    board = Board(decodeBoard(boardJSON))
    curPlayer = board.board["turn"]

    move = decideMove(g,board,curPlayer)

    encodedMove = json.dumps(move)
    print(encodedMove)
    await websocket.send(encodedMove)
    print("> responded with move")

start_server = websockets.serve(sendMove, 'localhost', 8765)
print("Listening at ws://127.0.0.1:8765")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
