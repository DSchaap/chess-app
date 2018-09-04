from Piece import Piece
import copy

class Game(object):
    """This class defines a chess game"""
    def __init__(self):
        self.board = {  ( 0,7 ):  Piece("Rook", -1, ( 0,7 ))
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
        }
        self.turn = 1 # 1 for White's turn and -1 for Black's
        self.whiteCastlingRights = (True,True) # Permanent (left, right) castling rights
        self.blackCastlingRights = (True,True)
        self.whiteKing = ( 7,4 ) # King position (easier for finding legal moves/checks quickly)
        self.blackKing = ( 0,4 )
        self.enPassant = None # Keeps track of en passant square if there is one (None if not)


    def legal_moves(self,color):
        """Returns a list of all legal moves for the current game state"""
        board = self.board
        allLegal = []
        for square in board.keys():
            piece = board[square]
            if (piece.color == color):
                for move in self.__legal_piece_moves(board[square]):
                    allLegal.append({"piece":board[square],"newPosition":move})
        return allLegal


    def game_over(self):
        if (self.legal_moves(self.turn) == []):
            if (self.turn == 1):
                kingPosition = self.whiteKing
            else:
                kingPosition = self.blackKing
                if (self.__is_in_check(self.board,kingPosition,self.turn)):
                    return -self.turn
                else:
                    return 0
        else:
            return 1e-15

    def make_move(self,piece,newPosition):
        board = self.board
        (oldRow,oldCol) = piece.position
        (newRow,newCol) = newPosition
        oldEnPassant = self.enPassant
        piece.position = newPosition
        if ((piece.denomination == "Pawn") and (newRow == 0 or newRow == 7)):
            piece.denomination = "Queen"
        board[newPosition] = piece
        board.pop((oldRow,oldCol))
        self.enPassant = None
        if (piece.denomination == "King"):
            if (piece.color == 1):
                self.whiteCastlingRights = (False,False)
                self.whiteKing = newPosition
            else:
                self.blackCastlingRights = (False,False)
                self.blackKing = newPosition
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
                    self.enPassant = (newRow+1,newCol)
                else:
                    self.enPassant = (newRow-1,newCol)
        elif (piece.denomination == "Rook"):
            if (piece.color == 1):
                (boolLeft,boolRight) = self.whiteCastlingRights
                if (oldCol == 0):
                    self.whiteCastlingRights = (boolLeft,False)
                elif (oldCol == 7):
                    self.whiteCastlingRights = (False,boolRight)
            else:
                (boolLeft,boolRight) = self.blackCastlingRights
                if (oldCol == 0):
                    self.blackCastlingRights = (boolLeft,False)
                elif (oldCol == 7):
                    self.blackCastlingRights = (False,boolRight)
        # Account for if rooks are captured to avoid key errors
        if (newPosition == (0,0)):
            (boolLeft,boolRight) = self.blackCastlingRights
            self.blackCastlingRights = (False, boolRight)
        elif (newPosition == (0,7)):
            (boolLeft,boolRight) = self.blackCastlingRights
            self.blackCastlingRights = (boolLeft, False)
        elif (newPosition == (7,0)):
            (boolLeft,boolRight) = self.whiteCastlingRights
            self.whiteCastlingRights = (False, boolRight)
        elif (newPosition == (7,7)):
            (boolLeft,boolRight) = self.blackCastlingRights
            self.whiteCastlingRights = (boolLeft, False)
        self.turn = self.__change_color(self.turn)


    def __try_move(self,piece,newPosition):
        """Updates and produces a new board to test for moving into checks.
        Quicker to check and doesn't update the current game state or
        account for castling rights, or a new en passant status.
        Doesn't need to try castling because all of that logic is
        built into __can_castle."""
        board = dict(self.board)
        (newRow,newCol) = newPosition
        board[newPosition] = piece
        board.pop(piece.position)
        if (piece.denomination == "Pawn"):
            if (newPosition == self.enPassant):
                if (piece.color == 1):
                    board.pop((newRow+1,newCol))
                else:
                    board.pop((newRow-1,newCol))
        return board

    def __is_in_check(self,board,kingPosition,color):
        """Returns True of the given color is in check and False otherwise"""
        return (kingPosition in self.__attacked_squares(board,self.__change_color(color)))

    def __can_castle(self,color):
        """Checks if castling is legal in the current game state
        for the given color (removes possibility of moving into/ through checks)"""
        board = self.board
        occupied = board.keys()
        if (color == 1):
            (row,col) = self.whiteKing
            (boolLeft,boolRight) = self.whiteCastlingRights
        else:
            (row,col) = self.blackKing
            (boolLeft,boolRight) = self.blackCastlingRights
        attacked = self.__attacked_squares(board,self.__change_color(color))
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
        enPassant = self.enPassant
        attacked = []
        for square in board.keys():
            piece = board[square]
            if (piece.color == color):
                attacked = attacked + piece.moves(board, enPassant)
        attacked = list(set(attacked))
        return attacked


    def __change_color(self,color):
        if (color == 1):
            return -1
        else:
            return 1

    def __filter_checks(self,piece):
        """Takes in a piece and filters all moves that are
        illegal due to moving into check."""
        moves = piece.moves(self.board,self.enPassant)
        color = piece.color
        legalMoves = []
        for move in moves:
            if (piece.denomination == "King"):
                if ( not (self.__is_in_check(self.__try_move(piece,move),move,color)) ):
                    legalMoves.append(move)
            else:
                if (color == 1):
                    if ( not (self.__is_in_check(self.__try_move(piece,move),self.whiteKing,color)) ):
                        legalMoves.append(move)
                else:
                    if ( not (self.__is_in_check(self.__try_move(piece,move),self.blackKing,color)) ):
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
