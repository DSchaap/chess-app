module Main exposing (main)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Dict exposing (..)
import List exposing (..)
import Set exposing (..)
import WebSocket
import Json.Encode exposing (..)
import Json.Decode exposing (..)


type alias Model = {
    board : Board
    , selectedPiece: Selection
    , turn: Color
    , gameOver: GameStatus
    , enPassant: EnPassantStatus
    , whiteKing: (Int, Int)
    , blackKing: (Int, Int)
    , legalMoves: List LegalMove
    , playerColor: Color
    , message : String
    }

type alias Board = Dict ( Int, Int ) Square

type alias Piece = {
    denomination: Denomination
    , color: Color
    , moved: Bool
    , position: ( Int, Int )
    }

type Square = Occupied Piece
    | Empty

type Selection = Selected Piece
    | None

type LegalMove = Move Piece (Int,Int)

type GameStatus = Checkmate
    | Stalemate
    | Active

type EnPassantStatus = No
  | Yes ( Int, Int )

initialBoard: Board
initialBoard = Dict.fromList [ ( ( 0,0 ), Occupied ( Piece Rook Black False ( 0,0 ) ) )
    , ( ( 1,0 ), Occupied ( Piece Knight Black False ( 1,0 ) ) )
    , ( ( 2,0 ), Occupied ( Piece Bishop Black False ( 2,0 ) ) )
    , ( ( 3,0 ), Occupied ( Piece King Black False ( 3,0 ) ) )
    , ( ( 4,0 ), Occupied ( Piece Queen Black False ( 4,0 ) ) )
    , ( ( 5,0 ), Occupied ( Piece Bishop Black False ( 5,0 ) ) )
    , ( ( 6,0 ), Occupied ( Piece Knight Black False ( 6,0 ) ) )
    , ( ( 7,0 ), Occupied ( Piece Rook Black False ( 7,0 ) ) )
    , ( ( 0,1 ), Occupied ( Piece Pawn Black False ( 0,1 ) ) )
    , ( ( 1,1 ), Occupied ( Piece Pawn Black False ( 1,1 ) ) )
    , ( ( 2,1 ), Occupied ( Piece Pawn Black False ( 2,1 ) ) )
    , ( ( 3,1 ), Occupied ( Piece Pawn Black False ( 3,1 ) ) )
    , ( ( 4,1 ), Occupied ( Piece Pawn Black False ( 4,1 ) ) )
    , ( ( 5,1 ), Occupied ( Piece Pawn Black False ( 5,1 ) ) )
    , ( ( 6,1 ), Occupied ( Piece Pawn Black False ( 6,1 ) ) )
    , ( ( 7,1 ), Occupied ( Piece Pawn Black False ( 7,1 ) ) )
    , ( ( 0,2 ), Empty )
    , ( ( 1,2 ), Empty )
    , ( ( 2,2 ), Empty )
    , ( ( 3,2 ), Empty )
    , ( ( 4,2 ), Empty )
    , ( ( 5,2 ), Empty )
    , ( ( 6,2 ), Empty )
    , ( ( 7,2 ), Empty )
    , ( ( 0,3 ), Empty )
    , ( ( 1,3 ), Empty )
    , ( ( 2,3 ), Empty )
    , ( ( 3,3 ), Empty )
    , ( ( 4,3 ), Empty )
    , ( ( 5,3 ), Empty )
    , ( ( 6,3 ), Empty )
    , ( ( 7,3 ), Empty )
    , ( ( 0,4 ), Empty )
    , ( ( 1,4 ), Empty )
    , ( ( 2,4 ), Empty )
    , ( ( 3,4 ), Empty )
    , ( ( 4,4 ), Empty )
    , ( ( 5,4 ), Empty )
    , ( ( 6,4 ), Empty )
    , ( ( 7,4 ), Empty )
    , ( ( 0,5 ), Empty )
    , ( ( 1,5 ), Empty )
    , ( ( 2,5 ), Empty )
    , ( ( 3,5 ), Empty )
    , ( ( 4,5 ), Empty )
    , ( ( 5,5 ), Empty )
    , ( ( 6,5 ), Empty )
    , ( ( 7,5 ), Empty )
    , ( ( 0,7 ), Occupied ( Piece Rook White False ( 0,7 ) ) )
    , ( ( 1,7 ), Occupied ( Piece Knight White False ( 1,7 ) ) )
    , ( ( 2,7 ), Occupied ( Piece Bishop White False ( 2,7 ) ) )
    , ( ( 3,7 ), Occupied ( Piece King White False ( 3,7 ) ) )
    , ( ( 4,7 ), Occupied ( Piece Queen White False ( 4,7 ) ) )
    , ( ( 5,7 ), Occupied ( Piece Bishop White False ( 5,7 ) ) )
    , ( ( 6,7 ), Occupied ( Piece Knight White False ( 6,7 ) ) )
    , ( ( 7,7 ), Occupied ( Piece Rook White False ( 7,7 ) ) )
    , ( ( 0,6 ), Occupied ( Piece Pawn White False ( 0,6 ) ) )
    , ( ( 1,6 ), Occupied ( Piece Pawn White False ( 1,6 ) ) )
    , ( ( 2,6 ), Occupied ( Piece Pawn White False ( 2,6 ) ) )
    , ( ( 3,6 ), Occupied ( Piece Pawn White False ( 3,6 ) ) )
    , ( ( 4,6 ), Occupied ( Piece Pawn White False ( 4,6 ) ) )
    , ( ( 5,6 ), Occupied ( Piece Pawn White False ( 5,6 ) ) )
    , ( ( 6,6 ), Occupied ( Piece Pawn White False ( 6,6 ) ) )
    , ( ( 7,6 ), Occupied ( Piece Pawn White False ( 7,6 ) ) )
    ]

initialModel: ( Model, Cmd Msg )
initialModel =
  let
    modelWithoutMoves = Model initialBoard None White Active No ( 3,7 ) ( 3,0 ) [] White ""
  in
    ( { modelWithoutMoves | legalMoves = allLegalMoves modelWithoutMoves White }, Cmd.none )


type Denomination = King
    | Queen
    | Rook
    | Bishop
    | Knight
    | Pawn

type Color = White
    | Black

-- update --

type Msg = SelectPiece Piece
    | MovePiece Int Int
    | NewMessage String

update: Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        SelectPiece piece ->
            if ( piece.color == model.turn ) then
                ( { model | selectedPiece = Selected piece }, Cmd.none )
            else
                ( model, Cmd.none )
        MovePiece row col ->
            case model.selectedPiece of
                Selected piece ->
                  let
                      newPiece = { piece | position = (row,col), moved = True, denomination = checkQueen piece col }
                      newBoard = moveCastleOrPassant newPiece piece.position
                          <|Dict.insert piece.position Empty
                            <| Dict.insert (row,col) ( Occupied newPiece ) model.board
                      enPassantStatus = checkEnPassant newPiece piece.position
                      newModel = {model | board = newBoard, enPassant = enPassantStatus}
                      newLegalMoves = allLegalMoves newModel <| changeColor model.turn
                  in
                    case piece.denomination of
                      King ->
                        case model.turn of
                          White ->
                            ( { model | board = newBoard, selectedPiece = None, turn = changeColor model.turn, enPassant = No, whiteKing = (row,col), gameOver = checkForMate newModel newLegalMoves <| changeColor model.turn, legalMoves = newLegalMoves} , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves)  )
                          Black ->
                            ( { model | board = newBoard, selectedPiece = None, turn = changeColor model.turn, enPassant = No, blackKing = (row,col), gameOver = checkForMate newModel newLegalMoves <| changeColor model.turn, legalMoves = newLegalMoves} , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
                      Pawn ->
                        ( { model | board = newBoard, selectedPiece = None, turn = changeColor model.turn, enPassant = enPassantStatus, gameOver = checkForMate newModel newLegalMoves <| changeColor model.turn, legalMoves = newLegalMoves } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
                      _ ->
                        ( { model | board = newBoard, selectedPiece = None, turn = changeColor model.turn, enPassant = No, gameOver = checkForMate newModel newLegalMoves <| changeColor newModel.turn, legalMoves = newLegalMoves } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
                None ->
                         ( model, Cmd.none )
        NewMessage message ->
          case (Json.Decode.decodeString moveDecoder message) of
            Ok ( Move piece newPosition ) ->
              update (MovePiece (Tuple.first newPosition) (Tuple.second newPosition) )
                <| Tuple.first (update (SelectPiece piece) model)
            Err errMsg ->
              ( { model | message = errMsg }, Cmd.none )

commandMsg: Color -> Color -> String -> Cmd Msg
commandMsg pieceColor playerColor message =
  if (pieceColor == playerColor) then
    WebSocket.send server message
  else
    Cmd.none

checkQueen: Piece -> Int -> Denomination
checkQueen piece row =
  case piece.denomination of
    Pawn ->
      if ( (row == 0) || (row == 7) ) then
        Queen
      else
        piece.denomination
    _ ->
      piece.denomination

checkEnPassant: Piece -> (Int,Int) -> EnPassantStatus
checkEnPassant piece (oldRow,oldCol) =
  let
    (newRow,newCol) = piece.position
  in
    if ( abs (oldCol - newCol) ) > 1 then
      case piece.color of
        Black ->
          Yes (newRow,newCol-1)
        White ->
          Yes (newRow,newCol+1)
    else
      No

checkForMate: Model -> List LegalMove -> Color -> GameStatus
checkForMate model moves color =
  if ( moves == [] ) then
    if isInCheck model color then
      Checkmate
    else
      Stalemate
  else
    Active


changeColor: Color -> Color
changeColor color =
    case color of
        Black ->
            White
        White ->
            Black

moveCastleOrPassant: Piece -> (Int,Int)-> Board -> Board
moveCastleOrPassant piece (oldRow,oldCol) board =
  let
    (newRow,newCol)  = piece.position
  in
    case piece.denomination of
      King ->
        if ( ( abs (newRow - oldRow ) ) > 1 ) then
          case piece.color of
            Black ->
              if (newRow == 1 ) then
                Dict.insert (0,0) Empty
                  <| Dict.insert (2,0) ( Occupied ( Piece Rook Black True ( 2,0 ) ) ) board
              else
                Dict.insert (7,0) Empty
                  <| Dict.insert (4,0) ( Occupied ( Piece Rook Black True ( 4,0 ) ) ) board
            White ->
              if (newRow == 1 ) then
                Dict.insert (0,7) Empty
                  <| Dict.insert (2,7) ( Occupied ( Piece Rook White True ( 2,7 ) ) ) board
              else
                Dict.insert (7,7) Empty
                  <| Dict.insert (4,7) ( Occupied ( Piece Rook White True ( 4,7 ) ) ) board
        else
          board
      Pawn ->
        if ( (newRow /= oldRow) ) then
          case piece.color of
            Black ->
              Dict.insert (newRow, newCol-1) Empty board
            White ->
              Dict.insert (newRow, newCol+1) Empty board
        else
          board
      _ ->
        board


-- view --
view: Model -> Html Msg
view model =
  div [] [div [ id "board" ] ( List.map ( viewRow model ) (List.range 0 7) )
    , div [] [text model.message] ]

viewRow: Model -> Int -> Html Msg
viewRow model row =
    div [   ] (List.map (viewSquare model row) (List.range 0 7))

viewSquare: Model -> Int -> Int -> Html Msg
viewSquare model row col =
    case model.selectedPiece of
        Selected selectedPiece ->
            case Dict.get ( row, col ) model.board of
                Just square ->
                    case square of
                        Occupied piece ->
                            if (piece.color == selectedPiece.color) then
                                if ( selectedPiece == piece ) then
                                    div [class "yellow" ] [ viewPiece piece ]
                                else
                                    div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
                            else if ( canMoveTo model selectedPiece row col ) then
                                div [class "red", onClick <| MovePiece row col ] [ viewPiece piece ]
                            else
                                div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
                        _ ->
                            if ( canMoveTo model selectedPiece row col ) then
                                div [class "red", onClick <| MovePiece row col ] [ ]
                            else
                                div [ class <| squareColor model row col  ] [ ]
                Nothing ->
                    div [ ] [ ]

        None ->
            case Dict.get ( row, col ) model.board of
                Just square ->
                    case square of
                        Occupied piece ->
                            div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
                        _ ->
                            div [ class <| squareColor model row col  ] [ ]
                Nothing ->
                    div [ ] [ ]

canMoveTo: Model -> Piece -> Int -> Int -> Bool
canMoveTo model piece row col =
  List.member ( Move piece (row,col) ) model.legalMoves

squareColor: Model -> Int -> Int -> String
squareColor model row col =
        case ( ( row + col ) % 2 ) of
            0 ->
                "black"
            1 ->
                "white"
            _ ->
                ""

viewPiece: Piece -> Html Msg
viewPiece piece =
    case piece.color of
        Black ->
            case piece.denomination of
                Pawn ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Chess_pdt45.svg/90px-Chess_pdt45.svg.png" ] []
                Knight ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Chess_ndt45.svg/90px-Chess_ndt45.svg.png" ] []
                Bishop ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Chess_bdt45.svg/90px-Chess_bdt45.svg.png" ] []
                Rook ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Chess_rdt45.svg/90px-Chess_rdt45.svg.png" ] []
                Queen ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Chess_qdt45.svg/90px-Chess_qdt45.svg.png" ] []
                King ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Chess_kdt45.svg/90px-Chess_kdt45.svg.png" ] []
        White ->
            case piece.denomination of
                Pawn ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Chess_plt45.svg/90px-Chess_plt45.svg.png" ] []
                Knight ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Chess_nlt45.svg/90px-Chess_nlt45.svg.png" ] []
                Bishop ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Chess_blt45.svg/90px-Chess_blt45.svg.png" ] []
                Rook ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Chess_rlt45.svg/90px-Chess_rlt45.svg.png" ] []
                Queen ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Chess_qlt45.svg/90px-Chess_qlt45.svg.png" ] []
                King ->
                    img [ src "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Chess_klt45.svg/90px-Chess_klt45.svg.png" ] []

-- piece movement --

pawnMoves: Model -> Piece -> Set (Int, Int)
pawnMoves model piece =
  let
    (row,col) = piece.position
  in
    case piece.color of
      White ->
        case piece.moved of
          False ->
            if ( isOccupied model (row,col-1) ) then
              Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col-1),(row-1,col-1)] )
            else
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col-1),(row,col-2)] )
                <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col-1),(row-1,col-1)] )
          True ->
            case model.enPassant of
              No ->
                Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col-1)] )
                  <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col-1),(row-1,col-1)] )
              Yes enPassantSquare ->
                Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col-1)] )
                  <| Set.union ( Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col-1),(row-1,col-1)] ) )
                  <| (Set.intersect ( Set.fromList [enPassantSquare] ) ( Set.fromList [(row+1,col-1),(row-1,col-1)] ) )

      Black ->
        case piece.moved of
          False ->
            if ( isOccupied model (row,col+1) ) then
              Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] )
            else
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col+1),(row,col+2)] )
                <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] )
          True ->
            case model.enPassant of
              No ->
                Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col+1)] )
                  <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] )
              Yes enPassantSquare ->
                Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row,col+1)] )
                  <| Set.union ( Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] ) )
                  <| (Set.intersect ( Set.fromList [enPassantSquare] ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] ) )

knightMoves: Model -> Piece -> Set (Int,Int)
knightMoves model piece =
  let
    (row,col) = piece.position
  in
      Set.intersect (Set.fromList <| Dict.keys model.board)
        <| Set.filter ( not << isOccupiedBy piece.color model ) (Set.fromList [ (row+1,col+2), (row-1,col+2), (row+1,col-2), (row-1,col-2), (row+2,col+1), (row-2,col+1), (row+2,col-1), (row-2,col-1) ])

bishopMoves: Model -> Piece -> Set (Int,Int)
bishopMoves model piece =
    Set.union (clearPath (1,1) model piece.position piece.color Set.empty)
      <| Set.union (clearPath (1,-1) model piece.position piece.color Set.empty)
      <| Set.union (clearPath (-1,1) model piece.position piece.color Set.empty)
        (clearPath (-1,-1) model piece.position piece.color Set.empty)

rookMoves: Model -> Piece -> Set (Int,Int)
rookMoves model piece  =
    Set.union (clearPath (0,1) model piece.position piece.color Set.empty)
    <| Set.union (clearPath (0,-1) model piece.position piece.color Set.empty)
    <| Set.union (clearPath (1,0) model piece.position piece.color Set.empty)
      (clearPath (-1,0) model piece.position piece.color Set.empty)

queenMoves: Model -> Piece -> Set (Int,Int)
queenMoves model piece =
  Set.union ( rookMoves model piece ) ( bishopMoves model piece )

kingMoves: Model -> Piece -> Set (Int,Int)
kingMoves model piece =
  let
    (row,col) = piece.position
  in
    Set.union
      ( Set.union ( canCastleRight model piece ) ( canCastleLeft model piece ) )
      <| Set.intersect (Set.fromList <| Dict.keys model.board)
        <| Set.filter ( not << isOccupiedBy piece.color model ) (Set.fromList [ (row+1,col+1), (row+1,col-1), (row-1,col+1), (row-1,col-1), (row,col+1), (row,col-1), (row+1,col), (row-1,col) ])

canCastleRight: Model -> Piece -> Set (Int,Int)
canCastleRight model king =
  case king.moved of
    True ->
      Set.empty
    False ->
      case king.color of
        White ->
          case Dict.get (0,7) model.board of
            Nothing ->
              Set.empty
            Just square ->
              case square of
                Empty ->
                  Set.empty
                Occupied piece ->
                      if ( not ( piece.moved || ( isOccupied model (1,7) ) || ( isOccupied model (2,7) ) ) ) then
                        Set.fromList [(1,7)]
                      else
                        Set.empty
        Black ->
          case Dict.get (0,0) model.board of
            Nothing ->
              Set.empty
            Just square ->
              case square of
                Empty ->
                  Set.empty
                Occupied piece ->
                      if ( not ( piece.moved || ( isOccupied model (1,0) ) || ( isOccupied model (2,0) ) ) ) then
                        Set.fromList [(1,0)]
                      else
                        Set.empty

canCastleLeft: Model -> Piece -> Set (Int,Int)
canCastleLeft model king =
  case king.moved of
    True ->
      Set.empty
    False ->
      case king.color of
        White ->
          case Dict.get (7,7) model.board of
            Nothing ->
              Set.empty
            Just square ->
              case square of
                Empty ->
                  Set.empty
                Occupied piece ->
                      if ( not ( piece.moved || ( isOccupied model (4,7) ) || ( isOccupied model (5,7) ) || ( isOccupied model (6,7) ) ) ) then
                        Set.fromList [(5,7)]
                      else
                        Set.empty
        Black ->
          case Dict.get (0,0) model.board of
            Nothing ->
              Set.empty
            Just square ->
              case square of
                Empty ->
                  Set.empty
                Occupied piece ->
                      if ( not ( piece.moved || ( isOccupied model (4,0) ) || ( isOccupied model (5,0) ) || ( isOccupied model (6,0) ) ) ) then
                        Set.fromList [(5,0)]
                      else
                        Set.empty

attackedByPiece: Model -> Color -> (Int, Int) -> Square -> Set (Int,Int) -> Set (Int,Int)
attackedByPiece model color const square initialSet =
  case square of
    Empty ->
      initialSet
    Occupied piece ->
      if (piece.color == color) then
        case piece.denomination of
          Pawn ->
            Set.union initialSet <| pawnMoves model piece
          Knight ->
            Set.union initialSet <| knightMoves model piece
          Bishop ->
            Set.union initialSet <| bishopMoves model piece
          Rook ->
            Set.union initialSet <| rookMoves model piece
          Queen ->
            Set.union initialSet <| queenMoves model piece
          King ->
            Set.union initialSet <| kingMoves model piece
      else
        initialSet

attackedSquares: Model -> Color -> Set (Int,Int)
attackedSquares model color =
  Dict.foldr (attackedByPiece model color) Set.empty model.board

legalPieceMoves: Model -> Piece -> List LegalMove
legalPieceMoves model piece =
  case piece.denomination of
    Pawn ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( pawnMoves model piece )
    Knight ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( knightMoves model piece )
    Bishop ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( bishopMoves model piece )
    Rook ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( rookMoves model piece )
    Queen ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( queenMoves model piece )
    King ->
      List.map (Move piece)
        <| Set.toList
        <| Set.filter ( not << resultsInSelfCheck model piece ) ( kingMoves model piece )

legalMovesBySquare: Model -> Color -> (Int, Int) -> Square -> List LegalMove -> List LegalMove
legalMovesBySquare model color const square initialList =
  case square of
    Empty ->
      initialList
    Occupied piece ->
      if (piece.color == color) then
        List.append initialList <| legalPieceMoves model piece
      else
        initialList

allLegalMoves: Model -> Color -> List LegalMove
allLegalMoves model color =
  Dict.foldr (legalMovesBySquare model color) [] model.board

-- checks and path clearance --

isInCheck:  Model -> Color -> Bool
isInCheck model color =
  case color of
    White ->
      Set.member model.whiteKing <| attackedSquares model Black
    Black ->
      Set.member model.blackKing <| attackedSquares model White

resultsInSelfCheck: Model -> Piece -> (Int,Int) -> Bool
resultsInSelfCheck model piece newPosition =
  let
      newPiece = { piece | position = newPosition }
      newBoard = Dict.insert piece.position Empty
          <| Dict.insert newPosition ( Occupied newPiece ) model.board
  in
    case piece.denomination of
      King ->
        case piece.color of
          White ->
            isInCheck { model | board = newBoard, whiteKing = newPosition } White
          Black ->
            isInCheck { model | board = newBoard, blackKing = newPosition } Black
      _ ->
        isInCheck { model | board = newBoard } piece.color


isOccupiedBy: Color -> Model -> (Int,Int) -> Bool
isOccupiedBy color model position =
  case Dict.get position model.board of
    Nothing ->
      False
    Just square ->
      case square of
        Empty ->
          False
        Occupied piece ->
          piece.color == color

isOccupied: Model -> (Int,Int) -> Bool
isOccupied model position =
  case Dict.get position model.board of
    Nothing ->
      False
    Just square ->
      case square of
        Empty ->
          False
        Occupied piece ->
          True

-- First arguement is a vector with direction to check for clearance in
-- Used to check paths that rooks, bishops, and queens can travel along
clearPath: (Int,Int) -> Model -> (Int, Int) -> Color -> Set (Int,Int) -> Set (Int,Int)
clearPath (v1,v2) model (row,col) pieceColor path =
    case Dict.get (row+v1,col+v2) model.board of
        Nothing ->
            path
        Just square ->
            case square of
                Empty ->
                    clearPath (v1,v2) model (row+v1,col+v2) pieceColor ( Set.insert (row+v1,col+v2) path )
                Occupied pieceInPath ->
                    if ( pieceInPath.color == pieceColor ) then
                        path
                    else
                        ( Set.insert (row+v1,col+v2) path )

-- subs --

subscriptions: Model -> Sub Msg
subscriptions model =
  WebSocket.listen server NewMessage

-- communication with server --
server: String
server = "ws://127.0.0.1:3000"

encodeMoves : List LegalMove -> String
encodeMoves legalMoves =
  Json.Encode.encode 0 ( Json.Encode.list (List.map encodeMove legalMoves) )

encodePiece: Piece -> Json.Encode.Value
encodePiece {denomination,color,moved,position} =
    Json.Encode.object
      [("denomination", Json.Encode.string (toString denomination) )
      , ("color", Json.Encode.string (toString color) )
      , ("moved", Json.Encode.bool moved )
      , ("position", Json.Encode.list ([ Json.Encode.int (Tuple.first position), Json.Encode.int (Tuple.second position)] ) )
      ]

encodeMove : LegalMove -> Json.Encode.Value
encodeMove ( Move piece position ) =
    Json.Encode.object
      [ ("piece", (encodePiece piece) )
      , ("newPosition", Json.Encode.list ([ Json.Encode.int (Tuple.first position), Json.Encode.int (Tuple.second position)] ) )
      ]

pieceDecoder : Decoder Piece
pieceDecoder =
    Json.Decode.map4 Piece
      ( field "denomination" denominationDecoder )
      ( field "color" colorDecoder )
      ( field "moved" Json.Decode.bool)
      ( field "position" positionDecoder )



colorDecoder : Decoder Color
colorDecoder =
    Json.Decode.string
        |> Json.Decode.andThen (\str ->
           case str of
                "Black" ->
                    Json.Decode.succeed Black
                "White" ->
                    Json.Decode.succeed White
                somethingElse ->
                    Json.Decode.fail <| "Unknown color: " ++ somethingElse
        )

denominationDecoder : Decoder Denomination
denominationDecoder =
    Json.Decode.string
        |> Json.Decode.andThen (\str ->
           case str of
                "Pawn" ->
                    Json.Decode.succeed Pawn
                "Knight" ->
                    Json.Decode.succeed Knight
                "Bishop" ->
                    Json.Decode.succeed Bishop
                "Rook" ->
                    Json.Decode.succeed Rook
                "Queen" ->
                    Json.Decode.succeed Queen
                "King" ->
                    Json.Decode.succeed King
                somethingElse ->
                    Json.Decode.fail <| "Unknown color: " ++ somethingElse
        )


positionDecoder : Decoder (Int, Int)
positionDecoder = Json.Decode.map2 (,) ( index 0 Json.Decode.int ) ( index 1 Json.Decode.int )

moveDecoder: Decoder LegalMove
moveDecoder =
  Json.Decode.map2 Move
    ( field "piece" pieceDecoder )
    ( field "newPosition" positionDecoder )

-- main --

main =
    Html.program
        {init = initialModel
        , update = update
        , view = view
        , subscriptions = subscriptions }
