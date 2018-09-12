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
    , turn: Color
    , whiteCastlingRights: (Bool,Bool)
    , blackCastlingRights: (Bool,Bool)
    , whiteKing: (Int, Int)
    , blackKing: (Int, Int)
    , enPassant: EnPassantStatus
    , selectedPiece: Selection
    , gameOver: GameStatus
    , legalMoves: List LegalMove
    , playerColor: Color
    , message : String
    }

type alias Board = Dict ( Int, Int ) Piece

type alias Piece = {
    denomination: Denomination
    , color: Color
    , position: ( Int, Int )
    }

type Selection = Selected Piece
    | None

type LegalMove = Move Piece (Int,Int)

type GameStatus = Checkmate
    | Stalemate
    | Active

type EnPassantStatus = No
  | Yes ( Int, Int )

-- board is indexed similarly to a matrix (0,0) is top left and (7,7) is bottom right
initialBoard: Board
initialBoard = Dict.fromList [ ( ( 0,7 ), ( Piece Rook Black ( 0,7 ) ) )
    , ( ( 0,6 ), ( Piece Knight Black ( 0,6 ) ) )
    , ( ( 0,5 ), ( Piece Bishop Black ( 0,5 ) ) )
    , ( ( 0,4 ), ( Piece King Black ( 0,4 ) ) )
    , ( ( 0,3 ), ( Piece Queen Black ( 0,3 ) ) )
    , ( ( 0,2 ), ( Piece Bishop Black ( 0,2 ) ) )
    , ( ( 0,1 ), ( Piece Knight Black ( 0,1 ) ) )
    , ( ( 0,0 ), ( Piece Rook Black ( 0,0 ) ) )
    , ( ( 1,0 ), ( Piece Pawn Black ( 1,0 ) ) )
    , ( ( 1,1 ), ( Piece Pawn Black ( 1,1 ) ) )
    , ( ( 1,2 ), ( Piece Pawn Black ( 1,2 ) ) )
    , ( ( 1,3 ), ( Piece Pawn Black ( 1,3 ) ) )
    , ( ( 1,4 ), ( Piece Pawn Black ( 1,4 ) ) )
    , ( ( 1,5 ), ( Piece Pawn Black ( 1,5 ) ) )
    , ( ( 1,6 ), ( Piece Pawn Black ( 1,6 ) ) )
    , ( ( 1,7 ), ( Piece Pawn Black ( 1,7 ) ) )
    , ( ( 7,7 ), ( Piece Rook White ( 7,7 ) ) )
    , ( ( 7,6 ), ( Piece Knight White ( 7,6 ) ) )
    , ( ( 7,5 ), ( Piece Bishop White ( 7,5 ) ) )
    , ( ( 7,4 ), ( Piece King White ( 7,4 ) ) )
    , ( ( 7,3 ), ( Piece Queen White ( 7,3 ) ) )
    , ( ( 7,2 ), ( Piece Bishop White ( 7,2 ) ) )
    , ( ( 7,1 ), ( Piece Knight White ( 7,1 ) ) )
    , ( ( 7,0 ), ( Piece Rook White ( 7,0 ) ) )
    , ( ( 6,0 ), ( Piece Pawn White ( 6,0 ) ) )
    , ( ( 6,1 ), ( Piece Pawn White ( 6,1 ) ) )
    , ( ( 6,2 ), ( Piece Pawn White ( 6,2 ) ) )
    , ( ( 6,3 ), ( Piece Pawn White ( 6,3 ) ) )
    , ( ( 6,4 ), ( Piece Pawn White ( 6,4 ) ) )
    , ( ( 6,5 ), ( Piece Pawn White ( 6,5 ) ) )
    , ( ( 6,6 ), ( Piece Pawn White ( 6,6 ) ) )
    , ( ( 6,7 ), ( Piece Pawn White ( 6,7 ) ) )
    ]

initialModel: ( Model, Cmd Msg )
initialModel =
  let
    modelWithoutMoves = Model initialBoard White (True,True) (True,True) ( 7,4 ) ( 0,4 ) No None Active [] White ""
  in
    if (modelWithoutMoves.turn == modelWithoutMoves.playerColor) then
      ( { modelWithoutMoves | legalMoves = allLegalMoves modelWithoutMoves }, Cmd.none )
    else
      ( { modelWithoutMoves | legalMoves = allLegalMoves modelWithoutMoves }, WebSocket.send server (encodeMoves <| allLegalMoves modelWithoutMoves) )


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
                      newPiece = { piece | position = (row,col), denomination = checkQueen piece row }
                      newBoard = moveCastleOrPassant newPiece piece.position
                          <|Dict.remove piece.position
                            <| Dict.insert (row,col) ( newPiece ) model.board
                      enPassantStatus = checkEnPassant newPiece piece.position
                      newModel = {model | board = newBoard, enPassant = enPassantStatus, selectedPiece = None, turn = changeColor model.turn, enPassant = enPassantStatus}
                      newLegalMoves = allLegalMoves newModel
                  in
                    case piece.denomination of
                      King ->
                        case model.turn of
                          White ->
                            ( { newModel | whiteKing = (row,col), gameOver = checkForMate newModel newLegalMoves, legalMoves = newLegalMoves, whiteCastlingRights = (False,False) } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves)  )
                          Black ->
                            ( { newModel | blackKing = (row,col), gameOver = checkForMate newModel newLegalMoves, legalMoves = newLegalMoves, blackCastlingRights = (False,False) } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
                      _ ->
                        case model.turn of
                          White ->
                            ( { newModel | gameOver = checkForMate newModel newLegalMoves, legalMoves = newLegalMoves, whiteCastlingRights = checkCastlingRights piece model.whiteCastlingRights } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
                          Black ->
                            ( { newModel | gameOver = checkForMate newModel newLegalMoves, legalMoves = newLegalMoves, blackCastlingRights = checkCastlingRights piece model.blackCastlingRights } , commandMsg piece.color model.playerColor (encodeMoves newLegalMoves) )
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
  case piece.denomination of
    Pawn ->
      let
        (newRow,newCol) = piece.position
      in
        if ( abs (oldRow - newRow) ) > 1 then
          case piece.color of
            Black ->
              Yes (newRow-1,newCol)
            White ->
              Yes (newRow+1,newCol)
        else
          No
    _ ->
      No

checkCastlingRights: Piece -> (Bool,Bool) -> (Bool,Bool)
checkCastlingRights piece (oldCastleLeft,oldCastleRight) =
  case piece.denomination of
    Rook ->
      let
        (row,col) = piece.position
      in
        if (col == 0) then
          (False, oldCastleRight)
        else if (col == 7) then
          (oldCastleLeft, False)
        else
          (oldCastleLeft,oldCastleRight)
    _ ->
      (oldCastleLeft,oldCastleRight)


checkForMate: Model -> List LegalMove -> GameStatus
checkForMate model moves =
  if ( moves == [] ) then
    if isInCheck model model.turn then
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
        if ( ( abs (newCol - oldCol ) ) > 1 ) then
          case piece.color of
            Black ->
              if (newCol == 6 ) then
                Dict.remove (0,7)
                  <| Dict.insert (0,5) ( Piece Rook Black ( 0,5 ) ) board
              else
                Dict.remove (0,0)
                  <| Dict.insert (0,3) ( Piece Rook Black ( 0,3 ) ) board
            White ->
              if (newCol == 6 ) then
                Dict.remove (7,7)
                  <| Dict.insert (7,5) ( Piece Rook White ( 7,5 ) ) board
              else
                Dict.remove (7,0)
                  <| Dict.insert (7,3) ( Piece Rook White ( 7,3 ) ) board
        else
          board
      Pawn ->
        if ( (newCol /= oldCol) ) then
          case piece.color of
            Black ->
              Dict.remove (newRow-1, newCol) board
            White ->
              Dict.remove (newRow+1, newCol) board
        else
          board
      _ ->
        board


-- view --
view: Model -> Html Msg
view model =
  div [] [div [ id "board" ] ( List.map ( viewRow model ) (List.range 0 7) )
    , div [] [] ]

viewRow: Model -> Int -> Html Msg
viewRow model row =
    div [ class "row"  ] (List.map (viewSquare model row) (List.range 0 7))

viewSquare: Model -> Int -> Int -> Html Msg
viewSquare model row col =
    case model.selectedPiece of
        Selected selectedPiece ->
            case Dict.get ( row, col ) model.board of
              Just piece ->
                if (piece.color == selectedPiece.color) then
                    if ( selectedPiece == piece ) then
                        div [class "yellow" ] [ viewPiece piece ]
                    else
                        div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
                else if ( canMoveTo model selectedPiece row col ) then
                    div [class "red", onClick <| MovePiece row col ] [ viewPiece piece ]
                else
                    div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
              Nothing ->
                if ( canMoveTo model selectedPiece row col ) then
                    div [class "red", onClick <| MovePiece row col ] [ ]
                else
                    div [ class <| squareColor model row col  ] [ ]

        None ->
            case Dict.get ( row, col ) model.board of
                Just piece ->
                    div [ class <| squareColor model row col, onClick (SelectPiece piece) ] [ viewPiece piece ]
                Nothing ->
                    div [ class <| squareColor model row col  ] [ ]

canMoveTo: Model -> Piece -> Int -> Int -> Bool
canMoveTo model piece row col =
  List.member ( Move piece (row,col) ) model.legalMoves

squareColor: Model -> Int -> Int -> String
squareColor model row col =
        case ( ( row + col ) % 2 ) of
            1 ->
                "black"
            0 ->
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
        if (row == 6) then
          if ( isOccupied model (row-1,col) ) then
            Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row-1,col+1),(row-1,col-1)] )
          else
            Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row-1,col),(row-2,col)] )
              <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row-1,col+1),(row-1,col-1)] )
        else
          case model.enPassant of
            No ->
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row-1,col)] )
                <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row-1,col+1),(row-1,col-1)] )
            Yes enPassantSquare ->
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row-1,col)] )
                <| Set.union ( Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row-1,col+1),(row-1,col-1)] ) )
                <| (Set.intersect ( Set.fromList [enPassantSquare] ) ( Set.fromList [(row-1,col+1),(row-1,col-1)] ) )
      Black ->
        if (row == 1) then
          if ( isOccupied model (row+1,col) ) then
            Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row+1,col-1)] )
          else
            Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row+1,col),(row+2,col)] )
              <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row-1,col+1)] )
        else
          case model.enPassant of
            No ->
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row+1,col)] )
                <| Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row+1,col-1)] )
            Yes enPassantSquare ->
              Set.union ( Set.filter (not << isOccupied model) <| Set.fromList [(row+1,col)] )
                <| Set.union ( Set.filter (isOccupiedBy (changeColor piece.color) model ) ( Set.fromList [(row+1,col+1),(row+1,col-1)] ) )
                <| (Set.intersect ( Set.fromList [enPassantSquare] ) ( Set.fromList [(row+1,col+1),(row+1,col-1)] ) )

knightMoves: Model -> Piece -> Set (Int,Int)
knightMoves model piece =
  let
    (row,col) = piece.position
  in
    Set.filter isOnBoard
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
    Set.filter isOnBoard
      <| Set.filter ( not << isOccupiedBy piece.color model ) (Set.fromList [ (row+1,col+1), (row+1,col-1), (row-1,col+1), (row-1,col-1), (row,col+1), (row,col-1), (row+1,col), (row-1,col) ])

canCastleRight: Model -> Piece -> Set (Int,Int)
canCastleRight model king =
  case king.color of
    White ->
      if (Tuple.second model.whiteCastlingRights) then
        let
          attacked = attackedSquares model Black
        in
          if ((not ((isOccupied model (7,5)) || (isOccupied model (7,6)))) && (not ((Set.member (7,4) attacked) || (Set.member (7,5) attacked) || (Set.member (7,6) attacked)))) then
            Set.fromList [(7,6)]
          else
            Set.empty
      else
        Set.empty
    Black ->
      if (Tuple.second model.blackCastlingRights) then
        let
          attacked = attackedSquares model White
        in
          if ((not ((isOccupied model (0,5)) || (isOccupied model (0,6)))) && (not ((Set.member (0,4) attacked) || (Set.member (0,5) attacked) || (Set.member (0,6) attacked)))) then
            Set.fromList [(0,6)]
          else
            Set.empty
      else
        Set.empty

canCastleLeft: Model -> Piece -> Set (Int,Int)
canCastleLeft model king =
  case king.color of
    White ->
      if (Tuple.first model.whiteCastlingRights) then
        let
          attacked = attackedSquares model Black
        in
          if ((not ((isOccupied model (7,1)) || (isOccupied model (7,2)) || (isOccupied model (7,3)))) && (not ((Set.member (7,2) attacked) || (Set.member (7,3) attacked) || (Set.member (7,4) attacked)))) then
            Set.fromList [(7,2)]
          else
            Set.empty
      else
        Set.empty
    Black ->
      if (Tuple.first model.blackCastlingRights) then
        let
          attacked = attackedSquares model White
        in
          if ((not ((isOccupied model (0,1)) || (isOccupied model (0,2)) || (isOccupied model (0,3)))) && (not ((Set.member (0,2) attacked) || (Set.member (0,3) attacked) || (Set.member (0,4) attacked)))) then
            Set.fromList [(0,2)]
          else
            Set.empty
      else
        Set.empty

attackedByPiece: Model -> Color -> (Int, Int) -> Piece -> Set (Int,Int) -> Set (Int,Int)
attackedByPiece model color const piece initialSet =
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
          <| Set.union (Set.union (canCastleLeft model piece) (canCastleRight model piece))
            <| Set.filter ( not << resultsInSelfCheck model piece ) ( kingMoves model piece )

legalMovesBySquare: Model -> Color -> (Int, Int) -> Piece -> List LegalMove -> List LegalMove
legalMovesBySquare model color const piece initialList =
  if (piece.color == color) then
    List.append initialList <| legalPieceMoves model piece
  else
    initialList

allLegalMoves: Model -> List LegalMove
allLegalMoves model =
  Dict.foldr (legalMovesBySquare model model.turn) [] model.board

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
      newBoard = Dict.remove piece.position
          <| Dict.insert newPosition ( newPiece ) model.board
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
    Just piece ->
      piece.color == color

isOccupied: Model -> (Int,Int) -> Bool
isOccupied model position =
  case Dict.get position model.board of
    Nothing ->
      False
    Just piece ->
      True

isOnBoard: (Int,Int) -> Bool
isOnBoard (row,col) =
  ((row > -1) && (col > -1) && (row < 8) && (col < 8))

-- First arguement is a vector that decides the direction to check
-- Used to check paths that rooks, bishops, and queens can travel along
clearPath: (Int,Int) -> Model -> (Int, Int) -> Color -> Set (Int,Int) -> Set (Int,Int)
clearPath (v1,v2) model (row,col) pieceColor path =
    case Dict.get (row+v1,col+v2) model.board of
        Nothing ->
          if (not (isOnBoard (row+v1,col+v2))) then
            path
          else
            clearPath (v1,v2) model (row+v1,col+v2) pieceColor ( Set.insert (row+v1,col+v2) path )
        Just piece ->
          if ( piece.color == pieceColor ) then
              path
          else
              ( Set.insert (row+v1,col+v2) path )

-- subs --

subscriptions: Model -> Sub Msg
subscriptions model =
  WebSocket.listen server NewMessage

-- communication with server --
server: String
server = "http://localhost:3000/"

encodeMoves : List LegalMove -> String
encodeMoves legalMoves =
  Json.Encode.encode 0 ( Json.Encode.list (List.map encodeMove legalMoves) )

encodePiece: Piece -> Json.Encode.Value
encodePiece {denomination,color,position} =
    Json.Encode.object
      [("denomination", Json.Encode.string (toString denomination) )
      , ("color", Json.Encode.string (toString color) )
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
    Json.Decode.map3 Piece
      ( field "denomination" denominationDecoder )
      ( field "color" colorDecoder )
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
