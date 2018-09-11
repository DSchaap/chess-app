from Piece import Piece
from Move import Move
import numpy as np

class Board(object):
    """This class defines a chess game state"""
    def __init__(self,board):
        self.board = board

    def legal_moves(self,player):
        """Returns a list of all legal moves for the current game state"""
        board = self.board
        allLegal = []
        for square in board.keys():
            if isinstance(square, tuple):
                piece = board[square]
                if (piece.color == player):
                    for move in self.__legal_piece_moves(piece):
                        allLegal.append(Move(piece,move))
        return allLegal

    def is_in_check(self,board,kingPosition,color):
        """Returns True of the given color is in check and False otherwise"""
        return (kingPosition in self.__attacked_squares(board,-1*color))

    def execute_move(self,inputBoard,move):
        """Returns the updated board state after making the input move"""
        oldBoard = inputBoard.board
        board = dict(oldBoard)
        piece = Piece(move.piece.denomination,move.piece.color,move.piece.position)
        newPosition = move.newSquare
        (oldRow,oldCol) = piece.position
        (newRow,newCol) = newPosition
        oldEnPassant = oldBoard["enPassant"]
        piece.position = newPosition
        if ((piece.denomination == "Pawn") and (newRow == 0 or newRow == 7)):
            piece.denomination = "Queen"
        board[newPosition] = piece
        board.pop((oldRow,oldCol))
        board["enPassant"] = None
        if (piece.denomination == "King"):
            if (piece.color == 1):
                board["whiteCastlingRights"] = (False,False)
                board["whiteKing"] = newPosition
            else:
                board["blackCastlingRights"] = (False,False)
                board["blackKing"] = newPosition
            if ((newCol-oldCol)>1):
                newRook = board[(newRow,7)]
                newRook.position = (newRow,newCol-1)
                board[(oldRow,newCol-1)] = newRook
                board.pop((newRow,7))
            elif ((newCol - oldCol)<-1):
                newRook = board[(newRow,0)]
                newRook.position = (newRow,newCol+1)
                board[(oldRow,newCol+1)] = newRook
                board.pop((newRow,0))
        elif (piece.denomination == "Pawn"):
            if (newPosition == oldEnPassant):
                if (piece.color == 1):
                    board.pop((newRow+1,newCol))
                else:
                    board.pop((newRow-1,newCol))
            if (abs(newRow-oldRow)>1):
                if (piece.color == 1):
                    board["enPassant"] = (newRow+1,newCol)
                else:
                    board["enPassant"] = (newRow-1,newCol)
        elif (piece.denomination == "Rook"):
            if (piece.color == 1):
                (boolLeft,boolRight) = board["whiteCastlingRights"]
                if (oldCol == 0):
                    board["whiteCastlingRights"] = (boolLeft,False)
                elif (oldCol == 7):
                    board["whiteCastlingRights"] = (False,boolRight)
            else:
                (boolLeft,boolRight) = board["blackCastlingRights"]
                if (oldCol == 0):
                    board["blackCastlingRights"] = (boolLeft,False)
                elif (oldCol == 7):
                    board["blackCastlingRights"] = (False,boolRight)
        # Account for if rooks are captured to avoid key errors
        if (newPosition == (0,0)):
            (boolLeft,boolRight) = board["blackCastlingRights"]
            board["blackCastlingRights"] = (False, boolRight)
        elif (newPosition == (0,7)):
            (boolLeft,boolRight) = board["blackCastlingRights"]
            board["blackCastlingRights"] = (boolLeft, False)
        elif (newPosition == (7,0)):
            (boolLeft,boolRight) = board["whiteCastlingRights"]
            board["whiteCastlingRights"] = (False, boolRight)
        elif (newPosition == (7,7)):
            (boolLeft,boolRight) = board["whiteCastlingRights"]
            board["whiteCastlingRights"] = (boolLeft, False)
        return Board(board)

    def __try_move(self,board,piece,newPosition):
        """Updates and produces a new board to test for moving into checks.
        Quicker to check and doesn't update the current game state or
        account for castling rights, or a new en passant status.
        Doesn't need to try castling because all of that logic is
        built into __can_castle."""
        newBoard = dict(board)
        (newRow,newCol) = newPosition
        newBoard[newPosition] = piece
        newBoard.pop(piece.position)
        if (piece.denomination == "Pawn"):
            if (newPosition == board["enPassant"]):
                if (piece.color == 1):
                    newBoard.pop((newRow+1,newCol))
                else:
                    newBoard.pop((newRow-1,newCol))
        return newBoard

    def __can_castle(self,color):
        """Checks if castling is legal in the current game state
        for the given color (removes possibility of moving into/ through checks)"""
        board = self.board
        occupied = board.keys()
        if (color == 1):
            (row,col) = board["whiteKing"]
            (boolLeft,boolRight) = board["whiteCastlingRights"]
        else:
            (row,col) = board["blackKing"]
            (boolLeft,boolRight) = board["blackCastlingRights"]
        attacked = self.__attacked_squares(board,-1*color)
        if boolLeft:
            if (not ( ((row,col-1) in occupied) or ((row, col-2) in occupied) or ((row, col-3) in occupied) ) ):
                if (not ( ((row,col) in attacked) or ((row,col-1) in attacked) or ((row, col-2) in attacked)) ):
                    canCastleLeft = True
                else:
                    canCastleLeft = False
            else:
                canCastleLeft = False
        else:
            canCastleLeft = False
        if boolRight:
            if (not ( ((row,col+1) in occupied) or ((row, col+2) in occupied) ) ):
                if (not ( ((row,col) in attacked) or ((row,col+1) in attacked) or ((row, col+2) in attacked)) ):
                    canCastleRight = True
                else:
                    canCastleRight = False
            else:
                canCastleRight = False
        else:
            canCastleRight = False
        return (canCastleLeft,canCastleRight)


    def __attacked_squares(self,board,color):
        """Returns a list of all squares attacked by any piece of the given color"""
        enPassant = board["enPassant"]
        attacked = []
        for square in board.keys():
            if isinstance(square, tuple):
                piece = board[square]
                if (piece.color == color):
                    attacked = attacked + piece.moves(board, enPassant)
        attacked = list(set(attacked))
        return attacked


    def __filter_checks(self,piece):
        """Takes in a piece and filters all moves that are
        illegal due to moving into check."""
        board = self.board
        moves = piece.moves(board,board["enPassant"])
        color = piece.color
        legalMoves = []
        for move in moves:
            if (piece.denomination == "King"):
                if ( not (self.is_in_check(self.__try_move(board,piece,move),move,color)) ):
                    legalMoves.append(move)
            else:
                if (color == 1):
                    if ( not (self.is_in_check(self.__try_move(board,piece,move),board["whiteKing"],color)) ):
                        legalMoves.append(move)
                else:
                    if ( not (self.is_in_check(self.__try_move(board,piece,move),board["blackKing"],color)) ):
                        legalMoves.append(move)
        return legalMoves


    def __legal_piece_moves(self,piece):
        """Accounts for castling when checking for possible moves"""
        moves = self.__filter_checks(piece)
        if piece.denomination == "King":
            (canCastleLeft,canCastleRight) = self.__can_castle(piece.color)
            (row,col) = piece.position
            if canCastleRight:
                moves.append((row,col+2))
            if canCastleLeft:
                moves.append((row,col-2))
        return moves