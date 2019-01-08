import unittest
from chessAI.Piece import Piece
from chessAI.Move import Move, one_hot_to_move
from chessAI.Board import Board
from chessAI.Game import Game

class BoardTestCase(unittest.TestCase):
    def setUp(self):
        # The following position is the result of
        # 1. d4 e5 2. d5 Bb4+ 3. Nc3 h6 4. Be3 Nf6 5. Qd3 c5
        self.game = Game()
        self.position1 = {  ( 0,7 ):  Piece("Rook", -1, ( 0,7 ))
                    , ( 2,5 ): Piece("Knight", -1, ( 2,5 ))
                    , ( 4,1 ): Piece("Bishop", -1, ( 4,1 ))
                    , ( 0,4 ): Piece("King" , -1 , ( 0,4 ))
                    , ( 0,3 ): Piece("Queen" , -1 , ( 0,3 ))
                    , ( 0,2 ): Piece("Bishop" , -1 , ( 0,2 ))
                    , ( 0,1 ): Piece("Knight" , -1 , ( 0,1 ))
                    , ( 0,0 ): Piece("Rook" , -1 , ( 0,0 ))
                    , ( 1,0 ): Piece("Pawn" , -1 , ( 1,0 ))
                    , ( 1,1 ): Piece("Pawn" , -1 , ( 1,1 ))
                    , ( 3,2 ): Piece("Pawn" , -1 , ( 3,2 ))
                    , ( 1,3 ): Piece("Pawn" , -1 , ( 1,3 ))
                    , ( 3,4 ): Piece("Pawn" , -1 , ( 3,4 ))
                    , ( 1,5 ): Piece("Pawn" , -1 , ( 1,5 ))
                    , ( 1,6 ): Piece("Pawn" , -1 , ( 1,6 ))
                    , ( 2,7 ): Piece("Pawn" , -1 , ( 2,7 ))
                    , ( 7,7 ): Piece("Rook" , 1 , ( 7,7 ))
                    , ( 7,6 ): Piece("Knight" , 1 , ( 7,6 ))
                    , ( 7,5 ): Piece("Bishop" , 1 , ( 7,5 ))
                    , ( 7,4 ): Piece("King" , 1 , ( 7,4 ))
                    , ( 5,3 ): Piece("Queen" , 1 , ( 5,3 ))
                    , ( 5,4 ): Piece("Bishop" , 1 , ( 5,4 ))
                    , ( 5,2 ): Piece("Knight" , 1 , ( 5,2 ))
                    , ( 7,0 ): Piece("Rook" , 1 , ( 7,0 ))
                    , ( 6,0 ): Piece("Pawn" , 1 , ( 6,0 ))
                    , ( 6,1 ): Piece("Pawn" , 1 , ( 6,1 ))
                    , ( 6,2 ): Piece("Pawn" , 1 , ( 6,2 ))
                    , ( 3,3 ): Piece("Pawn" , 1 , ( 3,3 ))
                    , ( 6,4 ): Piece("Pawn" , 1 , ( 6,4 ))
                    , ( 6,5 ): Piece("Pawn" , 1 , ( 6,5 ))
                    , ( 6,6 ): Piece("Pawn" , 1 , ( 6,6 ))
                    , ( 6,7 ): Piece("Pawn" , 1 , ( 6,7 ))
                    , "whiteCastlingRights": (True,True) # Permanent (left, right) castling rights
                    , "blackCastlingRights": (True,True)
                    , "whiteKing": ( 7,4 ) # King position (easier for finding legal moves/checks quickly)
                    , "blackKing": ( 0,4 )
                    , "enPassant": (2,2) # Keeps track of en passant square if there is one (None if not)
                    , "recentMoves": [(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]
                    , "turn": 1
                    }
        # Position after 6. a3
        self.position2 = {  ( 0,7 ):  Piece("Rook", -1, ( 0,7 ))
                    , ( 2,5 ): Piece("Knight", -1, ( 2,5 ))
                    , ( 4,1 ): Piece("Bishop", -1, ( 4,1 ))
                    , ( 0,4 ): Piece("King" , -1 , ( 0,4 ))
                    , ( 0,3 ): Piece("Queen" , -1 , ( 0,3 ))
                    , ( 0,2 ): Piece("Bishop" , -1 , ( 0,2 ))
                    , ( 0,1 ): Piece("Knight" , -1 , ( 0,1 ))
                    , ( 0,0 ): Piece("Rook" , -1 , ( 0,0 ))
                    , ( 1,0 ): Piece("Pawn" , -1 , ( 1,0 ))
                    , ( 1,1 ): Piece("Pawn" , -1 , ( 1,1 ))
                    , ( 3,2 ): Piece("Pawn" , -1 , ( 3,2 ))
                    , ( 1,3 ): Piece("Pawn" , -1 , ( 1,3 ))
                    , ( 3,4 ): Piece("Pawn" , -1 , ( 3,4 ))
                    , ( 1,5 ): Piece("Pawn" , -1 , ( 1,5 ))
                    , ( 1,6 ): Piece("Pawn" , -1 , ( 1,6 ))
                    , ( 2,7 ): Piece("Pawn" , -1 , ( 2,7 ))
                    , ( 7,7 ): Piece("Rook" , 1 , ( 7,7 ))
                    , ( 7,6 ): Piece("Knight" , 1 , ( 7,6 ))
                    , ( 7,5 ): Piece("Bishop" , 1 , ( 7,5 ))
                    , ( 7,4 ): Piece("King" , 1 , ( 7,4 ))
                    , ( 5,3 ): Piece("Queen" , 1 , ( 5,3 ))
                    , ( 5,4 ): Piece("Bishop" , 1 , ( 5,4 ))
                    , ( 5,2 ): Piece("Knight" , 1 , ( 5,2 ))
                    , ( 7,0 ): Piece("Rook" , 1 , ( 7,0 ))
                    , ( 5,0 ): Piece("Pawn" , 1 , ( 5,0 ))
                    , ( 6,1 ): Piece("Pawn" , 1 , ( 6,1 ))
                    , ( 6,2 ): Piece("Pawn" , 1 , ( 6,2 ))
                    , ( 3,3 ): Piece("Pawn" , 1 , ( 3,3 ))
                    , ( 6,4 ): Piece("Pawn" , 1 , ( 6,4 ))
                    , ( 6,5 ): Piece("Pawn" , 1 , ( 6,5 ))
                    , ( 6,6 ): Piece("Pawn" , 1 , ( 6,6 ))
                    , ( 6,7 ): Piece("Pawn" , 1 , ( 6,7 ))
                    , "whiteCastlingRights": (True,True) # Permanent (left, right) castling rights
                    , "blackCastlingRights": (True,True)
                    , "whiteKing": ( 7,4 ) # King position (easier for finding legal moves/checks quickly)
                    , "blackKing": ( 0,4 )
                    , "enPassant": None # Keeps track of en passant square if there is one (None if not)
                    , "recentMoves": [(self.position1[(6,0)].position,self.position1[(6,0)].denomination,(5,0)),(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,4,4)]
                    , "turn": -1
                    }
        self.board1 = Board(self.position1)
        self.board2 = Board(self.position2)
        self.move1 = Move(self.position1[( 5,3 )],(4,2))
        self.move2 = Move(self.position1[( 2,7 )],(3,7))
        self.move3 = Move(self.position1[( 5,4 )],(2,7))
        self.move4 = Move(self.position1[( 4,1 )],(5,2))

class TestPieceMoves(BoardTestCase):
    # Remember moves method of Piece does not check if move results in check
    # converting output to sets because order of moves reported does not matter
    def test_king(self):
        # Remember moves method of Piece does not include castling
        whiteKing = self.position1[( 7,4 )]
        blackKing = self.position1[( 0,4 )]
        self.assertEqual(set(whiteKing.moves(self.board1.board)),set([(7,3),(6,3)]))
        self.assertEqual(set(blackKing.moves(self.board1.board)),set([(1,4),(0,5)]))

    def test_queen(self):
        whiteQueen = self.position1[( 5,3 )]
        blackQueen = self.position1[( 0,3 )]
        self.assertEqual(set(whiteQueen.moves(self.board1.board)),set([(2,0),(3,1),(4,2),(4,3),(6,3),(7,3),(4,4),(3,5),(2,6),(1,7)]))
        self.assertEqual(set(blackQueen.moves(self.board1.board)),set([(3,0),(2,1),(1,2),(1,4)]))

    def test_rook(self):
        whiteRook1 = self.position1[( 7,7 )]
        whiteRook2 = self.position1[( 7,0 )]
        blackRook1 = self.position1[( 0,7 )]
        blackRook2 = self.position1[( 0,0 )]
        self.assertEqual(set(whiteRook1.moves(self.board1.board)),set([]))
        self.assertEqual(set(whiteRook2.moves(self.board1.board)),set([(7,1),(7,2),(7,3)]))
        self.assertEqual(set(blackRook1.moves(self.board1.board)),set([(0,5),(0,6),(1,7)]))
        self.assertEqual(set(blackRook2.moves(self.board1.board)),set([]))

    def test_bishop(self):
        whiteBishop1 = self.position1[( 7,5 )]
        whiteBishop2 = self.position1[( 5,4 )]
        blackBishop1 = self.position1[( 4,1 )]
        blackBishop2 = self.position1[( 0,2 )]
        self.assertEqual(set(whiteBishop1.moves(self.board1.board)),set([]))
        self.assertEqual(set(whiteBishop2.moves(self.board1.board)),set([(2,7),(3,2),(3,6),(4,3),(4,5),(6,3),(7,2)]))
        self.assertEqual(set(blackBishop1.moves(self.board1.board)),set([(3,0),(5,0),(5,2)]))
        self.assertEqual(set(blackBishop2.moves(self.board1.board)),set([]))

    def test_knight(self):
        # Note that whiteKnight2 is pinned but that is not accounted for yet
        whiteKnight1 = self.position1[( 7,6 )]
        whiteKnight2 = self.position1[( 5,2 )]
        blackKnight1 = self.position1[( 2,5 )]
        blackKnight2 = self.position1[( 0,1 )]
        self.assertEqual(set(whiteKnight1.moves(self.board1.board)),set([(5,5),(5,7)]))
        self.assertEqual(set(whiteKnight2.moves(self.board1.board)),set([(3,1),(4,0),(4,4),(7,1),(7,3)]))
        self.assertEqual(set(blackKnight1.moves(self.board1.board)),set([(0,6),(1,7),(3,3),(3,7),(4,4),(4,6)]))
        self.assertEqual(set(blackKnight2.moves(self.board1.board)),set([(2,0),(2,2)]))

    def test_pawn(self):
        whitePawn1 = self.position1[(6,0)]
        self.assertEqual(set(whitePawn1.moves(self.board1.board)),set([(5,0),(4,0)]))
        whitePawn2 = self.position1[(6,1)]
        self.assertEqual(set(whitePawn2.moves(self.board1.board)),set([(5,1)]))
        whitePawn3 = self.position1[(6,2)]
        self.assertEqual(set(whitePawn3.moves(self.board1.board)),set([]))
        whitePawn4 = self.position1[(3,3)]
        self.assertEqual(set(whitePawn4.moves(self.board1.board)),set([(2,3),(2,2)]))
        whitePawn5 = self.position1[(6,4)]
        self.assertEqual(set(whitePawn5.moves(self.board1.board)),set([]))
        whitePawn6 = self.position1[(6,5)]
        self.assertEqual(set(whitePawn6.moves(self.board1.board)),set([(5,5),(4,5)]))
        whitePawn7 = self.position1[(6,6)]
        self.assertEqual(set(whitePawn7.moves(self.board1.board)),set([(5,6),(4,6)]))
        whitePawn8 = self.position1[(6,7)]
        self.assertEqual(set(whitePawn8.moves(self.board1.board)),set([(5,7),(4,7)]))
        blackPawn1 = self.position1[(1,0)]
        self.assertEqual(set(blackPawn1.moves(self.board1.board)),set([(2,0),(3,0)]))
        # Skip black pawns 2 and 4 because of EnPassant and wrong turn making it confusing/ incorrect
        blackPawn3 = self.position1[(3,2)]
        self.assertEqual(set(blackPawn3.moves(self.board1.board)),set([(4,2)]))
        blackPawn5 = self.position1[(3,4)]
        self.assertEqual(set(blackPawn5.moves(self.board1.board)),set([(4,4)]))
        blackPawn6 = self.position1[(1,5)]
        self.assertEqual(set(blackPawn6.moves(self.board1.board)),set([]))
        blackPawn7 = self.position1[(1,6)]
        self.assertEqual(set(blackPawn7.moves(self.board1.board)),set([(2,6),(3,6)]))
        blackPawn8 = self.position1[(2,7)]
        self.assertEqual(set(blackPawn8.moves(self.board1.board)),set([(3,7)]))

class TestMoveMethods(BoardTestCase):
    def __is_same_move(self,move,newMoveTuple):
        piece,newSquare = newMoveTuple
        sameOldSquare = move.piece.position == piece.position
        sameDenomination = move.piece.denomination == piece.denomination
        sameColor = move.piece.color == piece.color
        sameNewSquare = move.newSquare == newSquare
        return (sameOldSquare and sameDenomination and sameColor and sameNewSquare)

    def test_inversion(self):
        self.assertTrue(self.__is_same_move(self.move1,one_hot_to_move(self.move1.one_hot(),self.board1,1,False)))
        self.assertTrue(self.__is_same_move(self.move2,one_hot_to_move(self.move2.one_hot(),self.board1,-1,False)))
        self.assertTrue(self.__is_same_move(self.move3,one_hot_to_move(self.move3.one_hot(),self.board1,1,False)))
        self.assertTrue(self.__is_same_move(self.move4,one_hot_to_move(self.move4.one_hot(),self.board1,-1,False)))

class TestBoardMethods(BoardTestCase):
    def __equal_pieces(self,piece1,piece2):
        sameDenomination = piece1.denomination == piece2.denomination
        sameColor = piece1.color == piece2.color
        sameSquare = piece1.position == piece2.position
        return (sameSquare and sameDenomination and sameColor)


    def __equal_boards(self,board1,board2):
        b1 = board1.board
        b2 = board2.board
        if b1.keys() != b2.keys():
            return False
        for k in b1.keys():
            if isinstance(k,tuple):
                if not self.__equal_pieces(b1[k],b2[k]):
                    return False
            else:
                if (b1[k]!=b2[k]):
                    return False
        return True


    def test_execute_move(self):
        self.assertTrue(self.__equal_boards(self.board2,self.board1.execute_move(self.board1,self.position1[(6,0)],(5,0),1)))
        self.assertFalse(self.__equal_boards(self.board2,self.board1.execute_move(self.board1,self.position1[(6,1)],(5,1),1)))

    def test_legal_moves(self):
        self.assertEqual(len(self.board1.legal_moves(1)),36)
        self.assertEqual(len(self.board2.legal_moves(-1)),31)

    def test_repetition(self):
        testBoard = self.board1.execute_move(self.board1.execute_move(self.board1.execute_move(self.board1.execute_move(self.board1.execute_move(self.board1,
            Piece("Bishop", 1, (5,4)),(6,3),1),
            Piece("Bishop", -1, (4,1)),(3,0),-1),
            Piece("Bishop", 1, (6,3)),(5,4),1),
            Piece("Bishop", -1, (3,0)),(4,1),-1),
            Piece("Bishop", 1, (5,4)),(6,3),1)
        repetitionBoard = self.board1.execute_move(testBoard,Piece("Bishop", -1, (4,1)),(3,0),-1)
        nonrepetitionBoard = self.board1.execute_move(testBoard,Piece("Bishop", -1, (4,1)),(5,2),-1)
        self.assertTrue(repetitionBoard.repetition())
        self.assertFalse(nonrepetitionBoard.repetition())

class TestGameMethods(BoardTestCase):
    def __equal_pieces(self,piece1,piece2):
        sameDenomination = piece1.denomination == piece2.denomination
        sameColor = piece1.color == piece2.color
        sameSquare = piece1.position == piece2.position
        return (sameSquare and sameDenomination and sameColor)

    def __equal_boards(self,board1,board2):
        b1 = board1.board
        b2 = board2.board
        if b1.keys() != b2.keys():
            return False
        for k in b1.keys():
            if isinstance(k,tuple):
                if not self.__equal_pieces(b1[k],b2[k]):
                    return False
            else:
                if (b1[k]!=b2[k]):
                    return False
        return True

    def testCanonicalForm(self):
        flippedPosition2 = {  ( 0,7 ):  Piece("Rook", -1, ( 0,7 ))
                    , ( 0,6 ): Piece("Knight", -1, ( 0,6 ))
                    , ( 0,5 ): Piece("Bishop", -1, ( 0,5 ))
                    , ( 0,4 ): Piece("King" , -1 , ( 0,4 ))
                    , ( 2,3 ): Piece("Queen" , -1 , ( 2,3 ))
                    , ( 2,4 ): Piece("Bishop" , -1 , ( 2,4 ))
                    , ( 2,2 ): Piece("Knight" , -1 , ( 2,2 ))
                    , ( 0,0 ): Piece("Rook" , -1 , ( 0,0 ))
                    , ( 2,0 ): Piece("Pawn" , -1 , ( 2,0 ))
                    , ( 1,1 ): Piece("Pawn" , -1 , ( 1,1 ))
                    , ( 1,2 ): Piece("Pawn" , -1 , ( 1,2 ))
                    , ( 4,3 ): Piece("Pawn" , -1 , ( 4,3 ))
                    , ( 1,4 ): Piece("Pawn" , -1 , ( 1,4 ))
                    , ( 1,5 ): Piece("Pawn" , -1 , ( 1,5 ))
                    , ( 1,6 ): Piece("Pawn" , -1 , ( 1,6 ))
                    , ( 1,7 ): Piece("Pawn" , -1 , ( 1,7 ))
                    , ( 7,7 ): Piece("Rook" , 1 , ( 7,7 ))
                    , ( 5,5 ): Piece("Knight" , 1 , ( 5,5 ))
                    , ( 3,1 ): Piece("Bishop" , 1 , ( 3,1 ))
                    , ( 7,4 ): Piece("King" , 1 , ( 7,4 ))
                    , ( 7,3 ): Piece("Queen" , 1 , ( 7,3 ))
                    , ( 7,2 ): Piece("Bishop" , 1 , ( 7,2 ))
                    , ( 7,1 ): Piece("Knight" , 1 , ( 7,1 ))
                    , ( 7,0 ): Piece("Rook" , 1 , ( 7,0 ))
                    , ( 6,0 ): Piece("Pawn" , 1 , ( 6,0 ))
                    , ( 6,1 ): Piece("Pawn" , 1 , ( 6,1 ))
                    , ( 4,2 ): Piece("Pawn" , 1 , ( 4,2 ))
                    , ( 6,3 ): Piece("Pawn" , 1 , ( 6,3 ))
                    , ( 4,4 ): Piece("Pawn" , 1 , ( 4,4 ))
                    , ( 6,5 ): Piece("Pawn" , 1 , ( 6,5 ))
                    , ( 6,6 ): Piece("Pawn" , 1 , ( 6,6 ))
                    , ( 5,7 ): Piece("Pawn" , 1 , ( 5,7 ))
                    , "whiteCastlingRights": (True,True) # Permanent (left, right) castling rights
                    , "blackCastlingRights": (True,True)
                    , "whiteKing": ( 7,4 ) # King position (easier for finding legal moves/checks quickly)
                    , "blackKing": ( 0,4 )
                    , "enPassant": None # Keeps track of en passant square if there is one (None if not)
                    , "recentMoves": [(self.position1[(6,0)].position,self.position1[(6,0)].denomination,(5,0)),(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,4,4)]
                    , "turn": 1
                    }
        self.assertTrue(self.__equal_boards(Board(flippedPosition2),self.game.getCanonicalForm(self.board2,-1)))
        self.assertTrue(self.__equal_boards(self.board1,self.game.getCanonicalForm(self.board1,1)))


    def testGameEnded(self):
        pass

    def testValidMoves(self):
        self.assertEqual(sum(self.game.getValidMoves(self.board1,1)),36)

    def testOne_hot(self):
        self.assertEqual(sum(self.game.one_hot(self.board1)),36)

if __name__ == '__main__':
    pieceSuite = unittest.TestLoader().loadTestsFromTestCase(TestPieceMoves)
    moveSuite = unittest.TestLoader().loadTestsFromTestCase(TestMoveMethods)
    boardSuite = unittest.TestLoader().loadTestsFromTestCase(TestBoardMethods)
    gameSuite = unittest.TestLoader().loadTestsFromTestCase(TestGameMethods)
    allTests = unittest.TestSuite([pieceSuite, moveSuite,boardSuite,gameSuite])
    unittest.TextTestRunner(verbosity=2).run(allTests)
