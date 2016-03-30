from leaflets.models import User


def render_form(handler, form, action):
    """Render the provided form to HTML.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Form form: the form to be rendered
    :param str action: the action to be undertaken upon submission of the form
    """
    form_template = """
    <form action="{action}" method="post">
        {xsrf}
        {fields}
        <input type="submit" value="{sign_in}">
    </form>"""
    return form_template.format(
        action=action,
        xsrf=handler.xsrf_form_html(),
        fields='\n'.join(
            [render_field(handler, field) for field in form._fields.values()]),
        sign_in=handler.locale.translate('sign in')
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
    return '<label>{label}</label>: {field}{errors}<br>'.format(
        label=handler.locale.translate(field.label.text),
        field=field,
        errors=render_errors(handler, field),
    )


def is_admin(handler):
    """Check whether the current user is an admin."""
    return handler.is_admin


def current_user_name(handler):
    """Get the name of the current user."""
    user_id = handler.get_current_user()
    if not user_id:
        return None

    user = User.query.get(user_id)
    return user and user.username
