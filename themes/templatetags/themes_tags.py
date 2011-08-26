from django import template

from themes.models import Theme, ThemeStaticFile
from themes import app_settings

register = template.Library()

class ThemeStaticFileNode(template.Node):
    name = None

    def __init__(self, name):
        self.name = template.Variable(name)

    def render(self, context):
        name = self.name.resolve(context)

        if ':' in name:
            theme, name  = name.split(':', 1)
            theme = Theme.objects.get(name=theme)
        elif 'request' in context and getattr(context['request'], 'theme', None):
            theme = context['request'].theme
        else:
            theme = Theme.objects.get_current()

        try:
            static_file = theme.static_files.get(name=name)
        except ThemeStaticFile.DoesNotExist:
            if app_settings.STATIC_NOT_FOUND_RETURNS_EMPTY:
                return ''
            else:
                raise

        return static_file.get_url()

def do_theme_static_file(parser, token):
    """
    Examples:
    
    {% theme_static_file "logo.gif" %}
    {% theme_static_file "theme-name:logo.gif" %}
    """
    bits = token.split_contents()
    return ThemeStaticFileNode(bits[1])
register.tag('theme_static_file', do_theme_static_file)

