function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text"),
        user = $(ev.target).closest('.user')[0],
        child = document.getElementById(data);

    // Don't copy into oneself, as that is pointless
    if(user == child || $('#' + user.id, child).length){
        return;
    }
    var children = $('> .children', user);
    if(children.length > 0){
       children = children[0];
    } else {
        // If there is no children div, add it
        var checkbox = document.createElement('input');
        checkbox.id = ev.target.dataset.userId + '-show-children';
        checkbox.setAttribute("type", "checkbox");
        checkbox.setAttribute("checked", true);

        // if the label is before the checkbox, the css won't work correctly. This
        // is a hack to change the order
        var label = user.children[0];
        user.appendChild(checkbox);
        user.appendChild(label);

        children = document.createElement('div')
        children.classList.add('children');
        user.appendChild(children);
    }
    children.appendChild(child);
    $('input[type="checkbox"]', user).prop('checked', true);

    // Update the database
    $.post('', {
        'user': child.dataset.userId,
        'target': user.dataset.userId,
        '_xsrf': $('input[name="_xsrf"]').val()
    });
}

$('.user').click(function(e){
    e.stopPropagation();
    if(e.target == this){
        $('input[type="checkbox"]', this).click()
    }
});

