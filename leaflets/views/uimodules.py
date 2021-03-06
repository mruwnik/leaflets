import re
from collections import defaultdict
from types import LambdaType, FunctionType

from leaflets.models import User, AddressStates, CampaignAddress


def render_form(handler, form, action, button):
    """Render the provided form to HTML.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Form form: the form to be rendered
    :param str action: the action to be undertaken upon submission of the form
    """
    form_template = """
    <form action="{action}" method="post" class="pure-form pure-form-aligned">
        {xsrf}
        <fieldset class="centered">
            {fields}
            <div class="pure-controls">
                <button type="submit" class="pure-button">{button}</button>
            </div>
        </fieldset>
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


def render_field(handler, field, **kwargs):
    """Render a single wtform field.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Field field: the field to be rendered
    """
    if field.type == 'HiddenField':
        return field(**kwargs)
    return """
        <div class="pure-control-group">
            <label>{label}</label> {field}{errors}
        </div>""".format(
        label=handler.locale.translate(field.label.text),
        field=field(**kwargs),
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

    return User.query.get(user_id)


def current_login(handler):
    """Get the login of the current user."""
    user = handler.current_user_obj
    return user and user.email


def link(url, text):
    return '<a href="%s">%s</a>' % (url, text)


def user_actions(handler, user):
    links = map(lambda parts: link(*parts), (
        (handler.reverse_url('add_user') + '?parent=%d' % user.id, handler.locale.translate('add user')),
        (handler.reverse_url('invite_users', user.id), handler.locale.translate('invite users')),
        (handler.reverse_url('edit_user') + '?user=%d' % user.id, handler.locale.translate('edit')),
    ))
    return '&nbsp;'.join(links)


DRAG_N_DROP = ' draggable="true" ondragstart="drag(event)" ondrop="drop(event)" ondragover="allowDrop(event)" '


def render_user(handler, user, editable=False, radio=False, is_parent=False):
    """Generate HTML for the given user."""
    checked = 'checked' if user.id == handler.current_user else ''
    if not is_parent:
        toggle = '<input type="checkbox" hidden %s id="%s-show-children"/>' % (checked, user.id)
    else:
        toggle = ''
    children = render_users(handler, user.children, editable, radio) if user.children else ''

    pending = ''
    if user.password_hash.startswith('reset-'):
        pending = '<span class="pending">(%s)</span>' % handler.locale.translate('pending_user')

    if radio:
        radio = '<input type="radio" hidden id="radio-{0}" value="{0}" name="child"/>'.format(user.id)

    return """{radio}
        <div id="user-{user_id}" class="user {classes}" data-user-id="{user_id}" {draggable}>
            {toggle}
            <label class="user-info">
                <div style="display: inline-block;">
                    <span class="name">{username}</span> {is_admin} {pending}<br>
                    <span class="email"> &lt;{email}&gt; </span>
                </div><br>
                <span>{actions}</span>
            </label>
            <div class="children">{children}</div>
        </div>
    """.format(
        radio=radio or '',
        classes='group' if children else '',
        draggable=DRAG_N_DROP if editable else '',
        toggle=toggle,
        user_id=user.id,
        username=user.username,
        email=user.email,
        actions=user_actions(handler, user) if (editable and not is_parent) else '',
        is_admin='(admin)' if user.admin else '',
        pending=pending,
        children=children,
    )


def render_parent(handler, parent, editable=False, radio=False):
    """Render a parent with all its children."""
    if not parent:
        return ''

    return render_user(handler, parent, editable, radio, is_parent=True)


def render_users(handler, users, editable=False, radio=False):
    """Render the given users."""
    if not users:
        return ''

    return '\n'.join([render_user(handler, user, editable, radio) for user in users])


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
    try:
        children = [checklist_item(contents[key]) for key in sorted(contents, key=house_comparator)]
        all_checked = all(map(lambda addr: addr.state == AddressStates.marked, contents.values()))
    except AttributeError:
        children = [checklist_level(key, contents[key], level + 1) for key in sorted(contents)]
        all_checked = False

    return CHECKLIST_LEVEL_TEMPLATE.format(
            level=level, id=item, label=item, html=''.join(children), level_class='checked' if all_checked else '')


def checklist_item(item):
    """Render a single checklist item."""
    selected = 'checked' if item.state == AddressStates.marked else ''
    return CHECKLIST_ITEM_TEMPLATE.format(id=item.address.id, selected=selected, contents=item.address.house)


def nested_checklist(handler, items):
    try:
        while items and len(items) == 1:
            items, = items.values()
    except TypeError:
        return checklist_item(items)

    return ''.join([checklist_level(key, items[key]) for key in sorted(items)])


def render_campaign_streets(handler, campaign):
    addrs_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(CampaignAddress)))
    for address in handler.get_addresses(campaign.id):
        addr = address.address
        addrs_tree[str(addr.town)][str(addr.street)][str(addr.house)] = address
    return nested_checklist(campaign, addrs_tree)
