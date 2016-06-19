function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text"),
        user = $(ev.target).closest('.user'),
        child = $('#' + data);

    // Don't copy into oneself, as that is pointless
    if(user == child || $('#' + user.id, child).length){
        return;
    }
    var children = $('> .children', user);
    if(!children.length){
        return;
    }

    oldParent = child.parent().closest('.user');
    child.appendTo(children);
    $('> input[type="checkbox"]', user).prop('checked', true);

    user.addClass('group');
    if(!oldParent.find('.user').length) {
        oldParent.removeClass('group');
    }

    // Update the database
    $.post('', {
        'user': child.data('userId'),
        'target': user.data('userId'),
        '_xsrf': $('input[name="_xsrf"]').val()
    });
}

$('div.user input').click(function(e){
    e.stopPropagation();
});

$('div.user, .user :not(input)').click(function(e){
    var user = $(this).closest('.user'),
        radio = $('input[name="child"][value="' + user.data('userId') + '"]'),
        checkbox = user.find('> input[type="checkbox"]');
    e.stopPropagation();
    if(!radio.length || radio.prop('checked')){
        checkbox.click();
    }
    radio.click();
});

