import legalMoves
import math
import random

initialBoard = {  ( 0,7 ):  { "denomination":"Rook", "color":"Black", "position":( 0,7 ) }
, ( 0,6 ): { "denomination":"Knight", "color":"Black", "position":( 0,6 ) }
, ( 0,5 ): { "denomination":"Bishop", "color":"Black", "position":( 0,5 ) }
, ( 0,4 ): { "denomination":"King" , "color":"Black" , "position":( 0,4 ) }
, ( 0,3 ): { "denomination":"Queen" , "color":"Black" , "position":( 0,3 ) }
, ( 0,2 ): { "denomination":"Bishop" , "color":"Black" , "position":( 0,2 ) }
, ( 0,1 ): { "denomination":"Knight" , "color":"Black" , "position":( 0,1 ) }
, ( 0,0 ): { "denomination":"Rook" , "color":"Black" , "position":( 0,0 ) }
, ( 1,0 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,0 ) }
, ( 1,1 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,1 ) }
, ( 1,2 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,2 ) }
, ( 1,3 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,3 ) }
, ( 1,4 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,4 ) }
, ( 1,5 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,5 ) }
, ( 1,6 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,6 ) }
, ( 1,7 ): { "denomination":"Pawn" , "color":"Black" , "position":( 1,7 ) }
, ( 7,7 ): { "denomination":"Rook" , "color":"White" , "position":( 7,7 ) }
, ( 7,6 ): { "denomination":"Knight" , "color":"White" , "position":( 7,6 ) }
, ( 7,5 ): { "denomination":"Bishop" , "color":"White" , "position":( 7,5 ) }
, ( 7,4 ): { "denomination":"King" , "color":"White" , "position":( 7,4 ) }
, ( 7,3 ): { "denomination":"Queen" , "color":"White" , "position":( 7,3 ) }
, ( 7,2 ): { "denomination":"Bishop" , "color":"White" , "position":( 7,2 ) }
, ( 7,1 ): { "denomination":"Knight" , "color":"White" , "position":( 7,1 ) }
, ( 7,0 ): { "denomination":"Rook" , "color":"White" , "position":( 7,0 ) }
, ( 6,0 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,0 ) }
, ( 6,1 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,1 ) }
, ( 6,2 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,2 ) }
, ( 6,3 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,3 ) }
, ( 6,4 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,4 ) }
, ( 6,5 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,5 ) }
, ( 6,6 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,6 ) }
, ( 6,7 ): { "denomination":"Pawn" , "color":"White" , "position":( 6,7 ) }
}

initialModel = { "board": initialBoard
, "turn":"White"
, "BlackCastlingRights": (True,True)
, "WhiteCastlingRights": (True,True)
, "BlackKing": ( 0,4 )
, "WhiteKing": ( 7,4 )
, "enPassant": None
}


pieceNotation = { "Pawn":""
, "Knight": "N"
, "Bishop":"B"
, "Rook":"R"
, "Queen":"Q"
, "King":"K"
}

def rowColTranslation(position):
    colTranslation = { 0: "a"
    , 1: "b"
    , 2: "c"
    , 3: "d"
    , 4: "e"
    , 5: "f"
    , 6: "g"
    , 7: "h"
    }
    rowTranslation = { 0: "8"
    , 1: "7"
    , 2: "6"
    , 3: "5"
    , 4: "4"
    , 5: "3"
    , 6: "2"
    , 7: "1"
    }
    (row,col) = position
    return (colTranslation[col] + rowTranslation[row])


def printMove(move):
    piece = move["piece"]
    newPosition = move["newPosition"]
    newRow,newCol = newPosition
    if (newCol == 8):
        print(newPosition)
    return (pieceNotation[piece["denomination"]] + rowColTranslation(newPosition))



game = []
model = initialModel
while len(game)<40:
    allLegal = legalMoves.allLegalMoves(model,model["turn"])
    moveNumber = int(math.floor(random.random()*len(allLegal)))
    move = allLegal[moveNumber]
    piece = move["piece"]
    newPosition = move["newPosition"]
    model = legalMoves.makeMove(model,piece,newPosition)
    print(printMove(move))
    game.append(printMove(move))

print(game)
