from django import template

from themes.models import Theme

register = template.Library()

class ThemeStaticFileURL(template.Node):
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

        static_file = theme.static_files.get(name=name)

        return static_file.get_url()

def do_theme_static_file_url(parser, token):
    """
    Examples:
    
    {% theme_static_file_url "logo.gif" %}
    {% theme_static_file_url "theme-name:logo.gif" %}
    """
    bits = token.split_contents()
    return ThemeStaticFileURL(bits[1])
register.tag('theme_static_file_url', do_theme_static_file_url)

