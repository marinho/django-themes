from django.template import get_library, import_library, InvalidTemplateLibrary, Template

class DjangoTemplate(Template):
    pass

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
    

