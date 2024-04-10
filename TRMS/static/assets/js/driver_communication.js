var socket = new WebSocket('ws://' + window.location.host + '/ws/communicate/');

socket.onopen = function(e) {
    console.log('Connection established!');
};


socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    // Handle incoming message
    console.log("Message from server: " + message);
};

socket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

function sendMessage(message) {
    socket.send(JSON.stringify({'message': message}));
}
