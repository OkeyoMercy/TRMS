    var socket = new WebSocket('ws://' + window.location.host + '/ws/communicate/');

    socket.onopen = function(e) {
        console.log('Connection established!');
    };
    socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        console.log("Message from server: " + message);
    };

    socket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    function sendMessage(message) {
        socket.send(JSON.stringify({'message': message}));
    }

    let url = 'ws://${windows.location.host}/ws/socket-server/'

    const chatsocket = new websocket (url)

    chatSocket.onmessage = function(e){
        let data = JSON.parse(e.data)
        console.log('Data:',data)
    }