class Piece(object):
    """This class defines a chess piece"""
    def __init__(self,denomination,color,position):
        """denomination: String representing denomination of piece
        color: 1 if White, -1 if Black
        position: Tuple with current position of piece on board """
        self.denomination = denomination
        self.color = color
        self.position = position

    def moves(self,board,enPassant):
        """Returns list of moves for any given piece
        according to only how basic piece movement rules work
        (not accounting for moves that depend on other piece positions, like
        moving into checks or castling)"""
        movesByPiece = { "Pawn": (lambda board: self.__pawn_moves(board,enPassant))
        , "Knight": self.__knight_moves
        , "Bishop": self.__bishop_moves
        , "Rook": self.__rook_moves
        , "Queen": self.__queen_moves
        , "King": self.__king_moves
       }
        return movesByPiece[self.denomination](board)

    def __clear_path(self,direction,board,currentSquare,pieceColor,path):
        """Checks for path of empty/ capturable squares in a direction
        for queen/rook/bishop moves"""
        (v1,v2) = direction
        (row,col) = currentSquare
        occupied = board.keys()
        if (not ((row+v1 in range(8)) and (col+v2 in range(8)))):
            return path
        else:
            if (row+v1 ,col+v2) in occupied:
                if (board[(row+v1 ,col+v2)].color == pieceColor):
                    return path
                else:
                    path.append((row+v1 ,col+v2))
                    return path
            else:
                path.append((row+v1 ,col+v2))
                return self.__clear_path(direction,board,(row+v1 ,col+v2),pieceColor,path)

    def __pawn_moves(self,board,enPassant):
        possible = []
        (row,col) = self.position
        occupied = board.keys()
        color = self.color
        if (color == 1):
            if (row == 6 ):
                if ((row-1,col) in occupied):
                    possible = (possible
                        + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row-1,col+1),(row-1,col-1)])))
                else:
                    possible = (possible
                        + list(filter(lambda x: (not x in occupied ),[(row-1,col),(row-2,col)]))
                        + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row-1,col+1),(row-1,col-1)])))
            else:
                possible = (possible
                    + list(filter(lambda x: (not x in occupied ),[(row-1,col)]))
                    + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row-1,col+1),(row-1,col-1)])))
            if (enPassant in [(row-1,col+1),(row-1,col-1)]):
                possible.append(enPassant)
        else:
            if (row == 1):
                if ((row+1,col) in occupied):
                    possible = (possible
                        + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row+1,col+1),(row+1,col-1)])))
                else:
                    possible = (possible
                        + list(filter(lambda x: (not x in occupied ),[(row+1,col),(row+2,col)]))
                        + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row+1,col+1),(row+1,col-1)])))
            else:
                possible = (possible
                    + list(filter(lambda x: (not x in occupied ),[(row+1,col)]))
                    + list(filter(lambda x: ( (x in occupied) and (board[x].color != color) ),[(row+1,col+1),(row+1,col-1)])))
            if (enPassant in [(row+1,col+1),(row+1,col-1)]):
                possible.append(enPassant)
        return possible

    def __knight_moves(self,board):
        possible = []
        (row,col) = self.position
        color = self.color
        occupied = board.keys()
        options = [ (row+1,col+2), (row-1,col+2), (row+1,col-2), (row-1,col-2), (row+2,col+1), (row-2,col+1), (row+2,col-1), (row-2,col-1) ]
        for move in options:
            if move in occupied:
                if (board[move].color == color):
                    pass
                else:
                    possible.append(move)
            else:
                if (move[0] in range(8) and move[1] in range(8)):
                    possible.append(move)
                else:
                    pass
        return possible


    def __bishop_moves(self,board):
        (row,col) = self.position
        color = self.color
        occupied = board.keys()
        possible = self.__clear_path((1,1),board,(row,col),color,[]) + self.__clear_path((-1,1),board,(row,col),color,[]) + self.__clear_path((1,-1),board,(row,col),color,[]) + self.__clear_path((-1,-1),board,(row,col),color,[])
        return possible


    def __rook_moves(self,board):
        (row,col) = self.position
        color = self.color
        occupied = board.keys()
        possible = self.__clear_path((1,0),board,(row,col),color,[]) + self.__clear_path((-1,0),board,(row,col),color,[]) + self.__clear_path((0,1),board,(row,col),color,[]) + self.__clear_path((0,-1),board,(row,col),color,[])
        return possible

    def __queen_moves(self,board):
        return list(set(self.__rook_moves(board)+self.__bishop_moves(board)))


    def __king_moves(self,board):
        possible = []
        (row,col) = self.position
        color = self.color
        occupied = board.keys()
        options =  [ (row+1,col+1), (row+1,col-1), (row-1,col+1), (row-1,col-1), (row,col+1), (row,col-1), (row+1,col), (row-1,col) ]
        for move in options:
            if move in occupied:
                if (board[move].color == self.color):
                    pass
                else:
                    possible.append(move)
            else:
                if (move[0] in range(8) and move[1] in range(8)):
                    possible.append(move)
                else:
                    pass
        return possible
