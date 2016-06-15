function markAddress(id, state) {
    var checkbox = $('.checklist-item input[value="' + id + '"]'),
        street = checkbox.parent().parent();

    checkbox.parent().removeClass('pending');
    checkbox.prop('checked', state == 'marked');
    if($('input:checkbox:not(:checked)', street).length == 0) {
        street.addClass('checked');
    } else {
        street.removeClass('checked');
    }
};


function initSocket() {
    var socket = new WebSocket(window.location.origin.replace('http', 'ws') + '/campaign/mark');

    socket.onmessage = function (event) {
        var address = JSON.parse(event.data);
        markAddress(address.id, address.state);
    };

    return socket;
};

/**
    Send a message to a websocket.

    If the socket has been disconnected, reconnect and resend the message.
 **/
function sendMessage(socket, message) {
    message = JSON.stringify(message);
    if (socket.readyState > 1) {
        socket = initSocket();
    }

    try {
        socket.send(message);
    } catch (err) {
        socket = initSocket();
        // Pretend to asynchronisly wait for the connection to be available.
        repeater = setTimeout(function(){
            if (socket.readyState < 1) { // 0 means that the connection is being initialised
                return;
            } else if (socket.readyState == 1) { // 1 means that the connection is receiving messages
                socket.send(message);
            }
            clearTimeout(repeater); // any value other than 0 should cause the function to finish
        }, 100);
    }
    return socket;
}


function postMessage(message) {
    var self = $(this);
    message['_xsrf'] = $('[name="_xsrf"]').val()

    self.parent().addClass('pending');
    $.post('', message).done(function(result){
        markAddress(message.address, message.state);
    });
}

try {
    var socket = initSocket();
    sender = function(message) { sendMessage(socket, message); };
} catch(err) {
    sender = postMessage;
}


$('.checklist-item input[type="checkbox"]').click(function(a, b, c){
    postMessage({
            'address': this.value,
            'state': (this.checked ? 'marked' : 'selected')
    });
});
