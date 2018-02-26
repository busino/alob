'''
Alob Project
2017
Author(s): R.Walker

'''
from django import http
from django.template import TemplateDoesNotExist, loader

ERROR_500_TEMPLATE_NAME = '500.html'


def server_error(message, template_name=ERROR_500_TEMPLATE_NAME):
    """
    500 error handler.

    Templates: :template:`500.html`
    Context: None
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_500_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return http.HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    return http.HttpResponseServerError(template.render(context=dict(message=message)))
