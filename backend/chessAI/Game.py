from chessAI.Piece import Piece
from chessAI.Board import Board
from chessAI.Move import one_hot_to_move
import numpy as np

class Game():
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.
    Use 1 for player1 and -1 for player2.
    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self):
        pass

    def getInitBoard(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        startBoard = {  ( 0,7 ):  Piece("Rook", -1, ( 0,7 ))
            , ( 0,6 ): Piece("Knight", -1, ( 0,6 ))
            , ( 0,5 ): Piece("Bishop", -1, ( 0,5 ))
            , ( 0,4 ): Piece("King" , -1 , ( 0,4 ))
            , ( 0,3 ): Piece("Queen" , -1 , ( 0,3 ))
            , ( 0,2 ): Piece("Bishop" , -1 , ( 0,2 ))
            , ( 0,1 ): Piece("Knight" , -1 , ( 0,1 ))
            , ( 0,0 ): Piece("Rook" , -1 , ( 0,0 ))
            , ( 1,0 ): Piece("Pawn" , -1 , ( 1,0 ))
            , ( 1,1 ): Piece("Pawn" , -1 , ( 1,1 ))
            , ( 1,2 ): Piece("Pawn" , -1 , ( 1,2 ))
            , ( 1,3 ): Piece("Pawn" , -1 , ( 1,3 ))
            , ( 1,4 ): Piece("Pawn" , -1 , ( 1,4 ))
            , ( 1,5 ): Piece("Pawn" , -1 , ( 1,5 ))
            , ( 1,6 ): Piece("Pawn" , -1 , ( 1,6 ))
            , ( 1,7 ): Piece("Pawn" , -1 , ( 1,7 ))
            , ( 7,7 ): Piece("Rook" , 1 , ( 7,7 ))
            , ( 7,6 ): Piece("Knight" , 1 , ( 7,6 ))
            , ( 7,5 ): Piece("Bishop" , 1 , ( 7,5 ))
            , ( 7,4 ): Piece("King" , 1 , ( 7,4 ))
            , ( 7,3 ): Piece("Queen" , 1 , ( 7,3 ))
            , ( 7,2 ): Piece("Bishop" , 1 , ( 7,2 ))
            , ( 7,1 ): Piece("Knight" , 1 , ( 7,1 ))
            , ( 7,0 ): Piece("Rook" , 1 , ( 7,0 ))
            , ( 6,0 ): Piece("Pawn" , 1 , ( 6,0 ))
            , ( 6,1 ): Piece("Pawn" , 1 , ( 6,1 ))
            , ( 6,2 ): Piece("Pawn" , 1 , ( 6,2 ))
            , ( 6,3 ): Piece("Pawn" , 1 , ( 6,3 ))
            , ( 6,4 ): Piece("Pawn" , 1 , ( 6,4 ))
            , ( 6,5 ): Piece("Pawn" , 1 , ( 6,5 ))
            , ( 6,6 ): Piece("Pawn" , 1 , ( 6,6 ))
            , ( 6,7 ): Piece("Pawn" , 1 , ( 6,7 ))
            , "whiteCastlingRights": (True,True) # Permanent (left, right) castling rights
            , "blackCastlingRights": (True,True)
            , "whiteKing": ( 7,4 ) # King position (easier for finding legal moves/checks quickly)
            , "blackKing": ( 0,4 )
            , "enPassant": None # Keeps track of en passant square if there is one (None if not)
            , "recentMoves": [(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]
            }
        return Board(startBoard)

    def one_hot(self,board):
        outVec = []
        for i in range(8):
            for j in range(8):
                if (i,j) in board.board.keys():
                    outVec = outVec + board.board[(i,j)].one_hot()
                else:
                    outVec = outVec + [0,0,0,0,0,0,0,0,0,0,0,0]
        outVec = outVec + [board.board["whiteCastlingRights"][0]*1, board.board["whiteCastlingRights"][1]*1]
        outVec = outVec + [board.board["blackCastlingRights"][0]*1, board.board["blackCastlingRights"][1]*1]
        return outVec


    # def getBoardSize(self):
    #     """
    #     Returns:
    #         (x,y): a tuple of board dimensions
    #     """
    #     pass

    def getActionSize(self):
        return 4096

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player as a one-hot vector
        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        piece,newPosition = one_hot_to_move(action,board,player)
        nextBoard = board.execute_move(board,piece,newPosition)
        nextPlayer = -1*player
        return nextBoard, nextPlayer

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player
        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        validMoves = np.zeros((4096,))
        for move in board.legal_moves(player):
            validMoves = validMoves + move.one_hot()
        return validMoves

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)
        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        if (board.legal_moves(player) == []):
            if (player == 1):
                kingPosition = board.board["whiteKing"]
            else:
                kingPosition = board.board["blackKing"]
            if (board.is_in_check(board.board,kingPosition,player)):
                return -player
            else:
                return 1e-12
        elif (board.noWins()):
            return 1e-12
        # elif (board.board["repetition"]):
        #     return 1e-12
        elif (board.repetition()):
            return 1e-12
            print("yes")
        else:
            return 0

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)
        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """

        if (player == 1):
            return board
        else:
            canonicalBoard = {}
            board = board.board
            for square in board.keys():
                if isinstance(square, tuple):
                    oldPiece = board[square]
                    piece = Piece(oldPiece.denomination,oldPiece.color,oldPiece.position)
                    (oldRow,oldCol) = piece.position
                    newRow = -oldRow + 7
                    newCol = oldCol
                    piece.color = -1*piece.color
                    piece.position = (newRow,newCol)
                    canonicalBoard[(newRow,newCol)] = piece
            canonicalBoard["whiteCastlingRights"] = board["blackCastlingRights"]
            canonicalBoard["blackCastlingRights"] = board["whiteCastlingRights"]
            if board["enPassant"] != None:
                (oldPassantRow,oldPassantCol) = board["enPassant"]
                newPassantRow = -oldPassantRow + 7
                newPassantCol = oldPassantCol
                canonicalBoard["enPassant"] = (newPassantRow,newPassantCol)
            else:
                canonicalBoard["enPassant"] = None
            (oldBKingRow,oldBKingCol) = board["blackKing"]
            newWKingRow = -oldBKingRow + 7
            newWKingCol = oldBKingCol
            canonicalBoard["whiteKing"] = (newWKingRow,newWKingCol)
            (oldWKingRow,oldWKingCol) = board["whiteKing"]
            newBKingRow = -oldWKingRow + 7
            newBKingCol = oldWKingCol
            canonicalBoard["blackKing"] = (newBKingRow,newBKingCol)
            canonicalBoard["recentMoves"] = board["recentMoves"]
            return Board(canonicalBoard)

    def getSymmetries(self, board, pi):
        return [(board,pi)]


    def stringRepresentation(self, board):
        """
        Input:
            board: current board
        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        boardString = str(self.one_hot(board))
        return boardString
