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


var socket = null;
function initSocket() {
    // set up a timer to check the connection every second
    setTimeout(initSocket, 1000);

    // don't do anything if it's already initialised
    if (socket && socket.readyState == socket.OPEN) {
        return socket;
    }
    socket = new WebSocket(window.location.origin.replace('http', 'ws') + '/campaign/mark');

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
function sendMessage(message) {
    message = JSON.stringify(message);

    try {
        socket.send(message);
    } catch (err) {
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
}


function postMessage(message) {
    var self = $(this);
    message['_xsrf'] = $('[name="_xsrf"]').val();

    self.parent().addClass('pending');
    $.post('', message).done(function(result){
        markAddress(message.address, message.state);
    });
}

try {
    initSocket();
    sender = function(message) { sendMessage(message); };
} catch(err) {
    sender = postMessage;
}


function updateItem(element) {
    $(element).parent().addClass('pending');
    sender({
        'campaign': $('[name="campaign_id"]').val(),
        'address': element.value,
        'state': (element.checked ? 'marked' : 'selected')
    }); 
}


$('.checklist-item input[type="checkbox"]').click(function(a, b, c){
    updateItem(this);
});
