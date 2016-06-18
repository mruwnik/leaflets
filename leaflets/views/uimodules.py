import re
from types import LambdaType
from operator import itemgetter

from leaflets.models import User, AddressStates


def render_form(handler, form, action, button):
    """Render the provided form to HTML.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Form form: the form to be rendered
    :param str action: the action to be undertaken upon submission of the form
    """
    form_template = """
    <form action="{action}" method="post">
        {xsrf}
        {fields}
        <input type="submit" value="{button}">
    </form>"""
    return form_template.format(
        action=action,
        xsrf=handler.xsrf_form_html(),
        fields='\n'.join(
            [render_field(handler, field) for field in form._fields.values()]),
        button=handler.locale.translate(button)
    )


def render_errors(handler, field):
    """Render all errors of a field.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Field field: the field to be rendered
    :rtype: str
    """
    if not field.errors:
        return ''

    error_msgs = '\n'.join(['<li>%s</li>' % handler.locale.translate(error) for error in field.errors])
    return '<ul class=errors>%s</ul>' % error_msgs


def render_field(handler, field):
    """Render a single wtform field.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Field field: the field to be rendered
    """
    if field.type == 'HiddenField':
        return str(field)
    return '<label>{label}</label>: {field}{errors}<br>'.format(
        label=handler.locale.translate(field.label.text),
        field=field,
        errors=render_errors(handler, field),
    )


def is_admin(handler):
    """Check whether the current user is an admin."""
    return handler.is_admin


def current_user_object(handler):
    """Get the current user."""
    user_id = handler.get_current_user()
    if not user_id:
        return None

    user = User.query.get(user_id)
    return user


def render_user(handler, user):
    """Generate HTML for the given user."""
    toggle, children = '', ''
    if user.children:
        checked = 'checked' if user.id == handler.current_user else ''
        toggle = '<input type="checkbox" %s id="%d-show-children"/>' % (checked, user.id)
        children = '<div class="children">%s</div>' % render_users(handler, user.children)

    return """
        <div id="user-{user_id}" class="user" data-user-id="{user_id}"
             draggable="true" ondragstart="drag(event)"
             ondrop="drop(event)" ondragover="allowDrop(event)">
            {toggle}
            <label for="{user_id}-show-children" class="user-info">
                <span>
                    <a href="{edit_user}">{username}</a> {is_admin}<br/>
                    <span class="email"> &lt;{email}&gt; </span>
                </span>
            </label>
            {children}
        </div>
    """.format(
        toggle=toggle,
        user_id=user.id,
        username=user.username,
        edit_user=handler.reverse_url('edit_user') + '?user=%d' % user.id,
        email=user.email,
        is_admin='(admin)' if user.admin else '',
        children=children,
    )


def render_users(handler, users):
    """Render the given users."""
    if not users:
        return ''

    return '\n'.join([render_user(handler, user) for user in users])


def house_comparator(house):
    """Compare house numbers so that they are sorted correctly.

    This is still incorrect, as numbers larger that 10**20 will not be sorted correctly, but that
    is so unlikely, that for most cases this should suffice.
    """
    try:
        number_parts = list(map(int, re.findall('\d+', house)))
        return re.sub('\d+', '%.20d', house) % tuple(number_parts)
    except (ValueError, TypeError):
        return house or ''


CHECKLIST_LEVEL_TEMPLATE = """
      <div id="checklist-{level}-{id}" class="checklist-level indented {level_class}">
            <input type="radio" name="level-{level}" id="level-{level}-{id}"/>
            <label for="level-{level}-{id}">{label}</label>
            {html}
        </div>
"""
CHECKLIST_ITEM_TEMPLATE = """
<div class="indented checklist-item">
    <input type="checkbox" name="checklist-item-{id}" id="checklist-item-{id}" value="{id}" {selected}/>
    <label for="checklist-item-{id}">{contents}</label>
</div>
"""


def checklist_level(item, contents, level=0):
    """Render a checklist level along with its children."""
    if contents.default_factory == LambdaType:
        children = [checklist_level(key, contents[key], level + 1) for key in sorted(contents)]
        all_checked = False
    else:
        children = [checklist_item(contents[key]) for key in sorted(contents, key=house_comparator)]
        all_checked = all(map(lambda addr: addr.state == AddressStates.marked, contents.values()))

    return CHECKLIST_LEVEL_TEMPLATE.format(
            level=level, id=item, label=item, html=''.join(children), level_class='checked' if all_checked else '')


def checklist_item(item):
    """Render a single checklist item."""
    selected = 'checked' if item.state == AddressStates.marked else ''
    return CHECKLIST_ITEM_TEMPLATE.format(id=item.address.id, selected=selected, contents=item.address.house)


def nested_checklist(handler, items, action_url=None):
    try:
        while items and len(items) == 1:
            items, = items.values()
    except TypeError:
        return checklist_item(items)

    return ''.join([checklist_level(key, items[key]) for key in sorted(items)])
