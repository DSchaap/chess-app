var WebSocketServer = require('websocket').server;
var http = require('http');

var server = http.createServer(function(request, response) {
  // process HTTP request. Since we're writing just WebSockets
  // server we don't have to implement anything.
});
server.listen(3000, function() {
  console.log('Listening at port 3000')
});

// create the server
wsServer = new WebSocketServer({
  httpServer: server
});


// WebSocket server
wsServer.on('request', function(request) {
  var connection = request.accept(null, request.origin);

  // This is the most important callback for us, we'll handle
  // all messages from users here.
  connection.on('message', function(message) {
    //console.log(message)
    var moves = JSON.parse(message.utf8Data)
    var moveNumber = Math.floor(Math.random() * moves.length );
    var selectedMove = moves[moveNumber]
    connection.sendUTF(JSON.stringify(selectedMove));
  });

  connection.on('close', function(connection) {
    // close user connection
  });
});
