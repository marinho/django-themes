from django import template

from themes.models import Theme

register = template.Library()

class ThemeStaticFileURL(template.Node):
    name = None
    theme = None

    def __init__(self, name, theme):
        self.name = template.Variable(name)
        self.theme = template.Variable(theme) if theme else None

    def render(self, context):
        name = self.name.resolve(context)

        if self.theme:
            theme = self.theme.resolve(context)
        else:
            theme = Theme.objects.get(is_default=True)

        static_file = theme.static_files.get(name=name)

        return static_file.get_url()

def do_theme_static_file_url(parser, token):
    """
    Examples:
    
    {% theme_static_file_url "logo.gif" %}
    {% theme_static_file_url "logo.gif" for "theme-name" %}
    """
    bits = token.split_contents()
    name = bits[1]
    theme = bits[3] if len(bits) > 3 else None
    return ThemeStaticFileURL(name, theme)
register.tag('theme_static_file_url', do_theme_static_file_url)

