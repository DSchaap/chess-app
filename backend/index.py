import asyncio
import websockets
import json
import numpy as np
from chessAI.Piece import Piece
from chessAI.Board import Board
from chessAI.Game import Game
from chessAI.NeuralNet import NeuralNet as nn
from chessAI.Move import one_hot_to_move

g = Game()
nnet = nn(g)

def decodeBoard(boardJSON):
    board = {}
    encodedBoard = json.loads(boardJSON)
    for key in encodedBoard["board"].keys():
        piece = encodedBoard["board"][key]
        board[eval(key)] = Piece(piece["denomination"],piece["color"],tuple(piece["position"]))
    board["whiteCastlingRights"] = tuple(encodedBoard["whiteCastlingRights"])
    board["blackCastlingRights"] = tuple(encodedBoard["whiteCastlingRights"])
    board["whiteKing"] = tuple(encodedBoard["whiteKing"])
    board["blackKing"] = tuple(encodedBoard["blackKing"])
    if encodedBoard["enPassant"] == None:
        board["enPassant"] = encodedBoard["enPassant"]
    else:
        board["enPassant"] = tuple(encodedBoard["enPassant"])
    board["turn"] = encodedBoard["turn"]
    return board

async def sendMove(websocket, path):
    boardJSON = await websocket.recv()
    print("< received board state")
    board = Board(decodeBoard(boardJSON))
    curPlayer = board.board["turn"]

    valids = g.getValidMoves(g.getCanonicalForm(board, curPlayer),1)
    one_hot = nnet.predict(g.one_hot(board))[0]
    move_vector = np.multiply(valids,one_hot)
    piece,(newRow,newCol) = one_hot_to_move(move_vector,board,curPlayer)

    move = {"piece":{"denomination":piece.denomination,"color":piece.color,"position":piece.position}, "newPosition":[int(newRow),int(newCol)]}
    encodedMove = json.dumps(move)
    await websocket.send(encodedMove)
    print("> responded with move")

start_server = websockets.serve(sendMove, 'localhost', 8765)
print("Listening at ws://127.0.0.1:8765")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
