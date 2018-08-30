'''
This module is only used for training the model by self play.
The actual app will receive legal moves from Elm along with
the board state each turn.
'''

#clear path

def clearPath(direction,model,origin,pieceColor,path):
    [v1,v2] = direction
    [row,col] = origin
    board = dict(model["board"])
    occupied = board.keys()
    if (not ((row+v1 in range(8)) and (col+v2 in range(8)))):
        return path
    else:
        if (row+v1 ,col+v2) in occupied:
            if (board[(row+v1 ,col+v2)]["color"] == pieceColor):
                return path
            else:
                path.append((row+v1 ,col+v2))
                return path
        else:
            path.append((row+v1 ,col+v2))
            return clearPath(direction,model,(row+v1 ,col+v2),pieceColor,path)



# moves by piece denomination

def pawnMoves(model,piece):
    possible = []
    [row,col] = piece["position"]
    board = model["board"]
    occupied = board.keys()
    color = piece["color"]
    if (color == "White"):
        if (row == 6 ):
            if ((row-1,col) in occupied):
                possible = (possible
                    + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row-1,col+1),(row-1,col-1)])))
            else:
                possible = (possible
                    + list(filter(lambda x: (not x in occupied ),[(row-1,col),(row-2,col)]))
                    + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row-1,col+1),(row-1,col-1)])))
        else:
            possible = (possible
                + list(filter(lambda x: (not x in occupied ),[(row-1,col)]))
                + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row-1,col+1),(row-1,col-1)])))
        if (model["enPassant"] in [(row-1,col+1),(row-1,col-1)]):
            possible.append(model["enPassant"])
    else:
        if (row == 1):
            if ((row+1,col) in occupied):
                possible = (possible
                    + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row+1,col+1),(row+1,col-1)])))
            else:
                possible = (possible
                    + list(filter(lambda x: (not x in occupied ),[(row+1,col),(row+2,col)]))
                    + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row+1,col+1),(row+1,col-1)])))
        else:
            possible = (possible
                + list(filter(lambda x: (not x in occupied ),[(row+1,col)]))
                + list(filter(lambda x: ( (x in occupied) and (board[x]["color"] != color) ),[(row+1,col+1),(row+1,col-1)])))
        if (model["enPassant"] in [(row+1,col+1),(row+1,col-1)]):
            possible.append(model["enPassant"])
    return possible

def knightMoves(model,piece):
    possible = []
    [row,col] = piece["position"]
    board = model["board"]
    occupied = board.keys()
    options = [ (row+1,col+2), (row-1,col+2), (row+1,col-2), (row-1,col-2), (row+2,col+1), (row-2,col+1), (row+2,col-1), (row-2,col-1) ]
    for move in options:
        if move in occupied:
            if (board[move]["color"] == piece["color"]):
                pass
            else:
                possible.append(move)
        else:
            if (move[0] in range(8) and move[1] in range(8)):
                possible.append(move)
            else:
                pass
    return possible


def bishopMoves(model,piece):
    [row,col] = piece["position"]
    color = piece["color"]
    board = model["board"]
    occupied = board.keys()
    possible = clearPath((1,1),model,(row,col),color,[]) + clearPath((-1,1),model,(row,col),color,[]) + clearPath((1,-1),model,(row,col),color,[]) + clearPath((-1,-1),model,(row,col),color,[])
    return possible


def rookMoves(model,piece):
    possible = []
    [row,col] = piece["position"]
    color = piece["color"]
    board = model["board"]
    occupied = board.keys()
    possible = clearPath((1,0),model,(row,col),color,[]) + clearPath((-1,0),model,(row,col),color,[]) + clearPath((0,1),model,(row,col),color,[]) + clearPath((0,-1),model,(row,col),color,[])
    return possible

def queenMoves(model,piece):
    return list(set(rookMoves(model,piece)+bishopMoves(model,piece)))


def kingMoves(model,piece):
    possible = []
    [row,col] = piece["position"]
    board = model["board"]
    color = piece["color"]
    occupied = board.keys()
    options =  [ (row+1,col+1), (row+1,col-1), (row-1,col+1), (row-1,col-1), (row,col+1), (row,col-1), (row+1,col), (row-1,col) ]
    for move in options:
        if move in occupied:
            if (board[move]["color"] == piece["color"]):
                pass
            else:
                possible.append(move)
        else:
            if (move[0] in range(8) and move[1] in range(8)):
                possible.append(move)
            else:
                pass
    return possible


def canCastle(model,color):
    board = model["board"]
    occupied = board.keys()
    (row,col) = model[color+"King"]
    attacked = attackedSquares(model,changeColor(color))
    (boolLeft,boolRight) = model[color+"CastlingRights"]
    if boolRight:
        if (not ( ((row,col-1) in occupied) or ((row, col-2) in occupied)) ):
            if (not ( ((row,col) in attacked) or ((row,col-1) in attacked) or ((row, col-2) in attacked)) ):
                canCastleRight = True
            else:
                canCastleRight = False
        else:
            canCastleRight = False
    else:
        canCastleRight = False
    if boolLeft:
        if (not ( ((row,col+1) in occupied) or ((row, col+2) in occupied) or ((row, col+3) in occupied) ) ):
            if (not ( ((row,col) in attacked) or ((row,col+1) in attacked) or ((row, col+2) in attacked)) ):
                canCastleLeft = True
            else:
                canCastleLeft = False
        else:
            canCastleLeft = False
    else:
        canCastleLeft = False
    return (canCastleLeft,canCastleRight)


# attackedSquares and checks

correctMoves = { "Pawn":pawnMoves
, "Knight": knightMoves
, "Bishop": bishopMoves
, "Rook": rookMoves
, "Queen": queenMoves
, "King": kingMoves
}

def attackedSquares(model,color):
    board = model["board"]
    attacked = []
    for square in board.keys():
        if (board[square]["color"] == color):
            attacked = attacked + pieceMoves(model,board[square])
    attacked = list(set(attacked))
    return attacked

def isInCheck(model,color):
    return (model[color+'King'] in attackedSquares(model,changeColor(color)))

def filterChecks(model,piece,moves):
    color = piece["color"]
    legalMoves = []
    for move in moves:
        if ( not isInCheck(makeMove(model,piece,move),color) ):
            legalMoves.append(move)
    return legalMoves

def changeColor(color):
    if (color == "White"):
        return "Black"
    else:
        return "White"

# legal moves and making moves

def allLegalMoves(model,color):
    board = model["board"]
    allLegal = []
    for square in board.keys():
        if board[square]["color"] == color:
            for move in legalPieceMoves(model,board[square]):
                allLegal.append({"piece":board[square],"newPosition":move})
    return allLegal

def pieceMoves(model,piece):
    return correctMoves[piece["denomination"]](model,piece)

def legalPieceMoves(model,piece):
    moves = filterChecks(model,piece,pieceMoves(model,piece))
    if piece["denomination"] == "King":
        (canCastleLeft,canCastleRight) = canCastle(model,piece["color"])
        (row,col) = piece["position"]
        if canCastleRight:
            moves.append((row,col-2))
        if canCastleLeft:
            moves.append((row,col+2))
    return moves


def makeMove(model,piece,newPosition):
    newModel = dict(model)
    board = dict(model["board"])
    newPiece = dict(piece)
    newPiece["position"] = newPosition
    (newRow,newCol) = newPosition
    if ((piece["denomination"] == "Pawn") and (newRow == 0 or newRow == 7)):
        newPiece["denomination"] = "Queen"
    board[newPosition] = newPiece
    board.pop(piece["position"])
    newModel["enPassant"] = None
    if (piece["denomination"] == "King"):
        newModel[piece["color"] + "CastlingRights"] = (False,False)
        newModel[piece["color"]+"King"] = newPosition
        (oldRow,oldCol) = piece["position"]
        if ((newCol-oldCol)>1):
            newRook = dict(board[(newRow,7)])
            newRook["position"] = (newRow,newCol-1)
            board[(oldRow,newCol-1)] = newRook
            board.pop((newRow,7))
        elif ((newCol - oldCol)<-1):
            newRook = dict(board[(newRow,0)])
            newRook["position"] = (newRow,newCol+1)
            board[(oldRow,newCol+1)] = newRook
            board.pop((newRow,0))
    elif (piece["denomination"] == "Pawn"):
        (oldRow,oldCol) = piece["position"]
        if (newPosition == model["enPassant"]):
            if (piece["color"] == "White"):
                board.pop((newRow+1,newCol))
            else:
                board.pop((newRow-1,newCol))
        if (abs(newRow-oldRow)>1):
            if (piece["color"] == "White"):
                newModel["enPassant"] = (newRow+1,newCol)
            else:
                newModel["enPassant"] = (newRow-1,newCol)
    elif (piece["denomination"] == "Rook"):
        (oldRow,oldCol) = piece["position"]
        (boolLeft,boolRight) = model[piece["color"]+"CastlingRights"]
        if (oldCol == 0):
            newModel[piece["color"]+"CastlingRights"] = (boolLeft,False)
        elif (oldCol == 7):
            newModel[piece["color"] + "CastlingRights"] = (False,boolRight)
    newModel["board"] = board
    newModel["turn"] = changeColor(model["turn"])
    return newModel
