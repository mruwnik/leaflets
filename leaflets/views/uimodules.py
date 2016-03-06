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


def render_field(handler, field):
    """Render a single wtform field.

    :param RequestHandler handler: the handler that is rendering the form
    :param wtforms.Field field: the field to be rendered
    """
    errors = ''
    if field.errors:
        error_msgs = '\n'.join(['<li>%s</li>' % error for error in field.errors])
        errors = '<ul class=errors>%s</ul>' % error_msgs

    return '<label>{label}</label>: {field}{errors}<br>'.format(
        label=field.label,
        field=field,
        errors=errors,
    )

