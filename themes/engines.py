import re

from django.template import get_library, import_library, InvalidTemplateLibrary, Template
from django.template.context import RequestContext

from registration import _registered_templates
import app_settings

EXP_TAGS = re.compile('({%[ ]+(extends|include|theme_static_file)[ ]+"(.+?)"[ ]+%})')

class DjangoTemplate(Template):
    registered_template = None

    def __init__(self, template_string, origin=None, name='<Unknown Template>'):
        self.theme_name, self.origin_name = origin.split(':')
        self.registered_template = _registered_templates.get(name, {})

        # Treat the values for tags 'extends', 'include' and 'theme_static_file'.
        for full, tag, value in EXP_TAGS.findall(template_string):
            if ':' not in value:
                new_value = full.replace('"'+value+'"', '"%s:%s"'%(self.theme_name, value))
                template_string = template_string.replace(full, new_value)

        super(DjangoTemplate, self).__init__(template_string, origin, name)

    def render(self, context):
        """
        This is important to treat the block context variables.
        """

        # Creates a new context for this rendering, removing excluded variables
        new_context = context.__copy__()
        exc_vars = (self.registered_template.get('excluded_variables', None) or
                app_settings.EXCLUDED_VARIABLES)
        for k in (exc_vars or []):
            for d in new_context.dicts:
                if k in d:
                    del d[k]

        return super(DjangoTemplate, self).render(new_context)

#---------------------------------------------------------------------------------------------
# The code using Jinja2 was partially copied from the package "django-jinja2loader":
# 
# https://github.com/nathforge/django-jinja2loader/blob/master/src/jinja2loader/__init__.py
#---------------------------------------------------------------------------------------------

try:
    import jinja2
except ImportError:
    jinja2 = None

if jinja2:
    def load_django_filters(filters, library_names, use_default_filters):
        
        if use_default_filters:
            library = import_library('django.template.defaultfilters')
            
            if not library:
                raise InvalidTemplateLibrary('Couldn\'t load django.template.defaultfilters')
            
            # Update the dict for filters that don't already exist, i.e
            # jinja2's built-in filters.
            filters.update(dict(
                (name, value)
                for (name, value)
                in library.filters.iteritems()
                if name not in filters
            ))
        
        for name in library_names:
            filters.update(get_library(name).filters)


    class Jinja2Template(jinja2.Template):
        def render(self, context):
            context_dict = {}
            for dct in context.dicts:
                context_dict.update(dct)
            return super(Jinja2Template, self).render(context_dict)

    #jinja2_env = jinja2.Environment(
    #    loader=jinja2.FileSystemLoader(TEMPLATE_DIRS),
    #    extensions=EXTENSIONS,
    #    autoescape=True,
    #)
    #
    #load_django_filters(
    #    jinja2_env.filters,
    #    library_names=DJANGO_FILTER_LIBRARIES,
    #    use_default_filters=USE_DEFAULT_DJANGO_FILTERS,
    #)
    #
    #jinja2_env.globals.update(GLOBALS)
    #jinja2_env.template_class = Template
    

