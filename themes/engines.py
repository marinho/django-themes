import re

from django.template import get_library, import_library, InvalidTemplateLibrary, Template
from django.template.context import RequestContext

import app_settings
from registration import get_registered_template
from exceptions import UnavailableLoad, UnavailableTag, UnavailableFilter, UnavailableInclude

EXP_TAGS = re.compile('({%[ ]*(extends|include|theme_static_file)[ ]+"(.+?)"[ ]*%})')
EXP_THEME_TAG = re.compile('{%[ ]*load[ ]+theme_static_file[ ]+.+?%}') # FIXME: This is not perfect (the optional space before the %})
EXP_EXTENDS = re.compile('({%[ ]*extends[ ]+.*?%})')
EXP_AV_LOAD = re.compile('{%[ ]*load[ ]+([\w_ -]+)[ ]*%}')
EXP_AV_TAG = re.compile('{%[ ]*([\w_]+)? ')
EXP_AV_FILTER = re.compile('{{[^}|]+\|([^ %}]+)')
EXP_AV_INCLUDE = re.compile('{%[ ]*include[ ]+"(.+?)"[ ]*%}')
ALL = '*'
DEFAULT_TAGS_NODES = {
        'for': ['endfor','empty'],
        'ifequal': ['else','endifequal'],
        'with': ['endwith'],
        'ifnotequal': ['else','endifnotequal'],
        'ifchanged': ['else','endifchanged'],
        'filter': ['endfilter'],
        'if': ['else','endif'],
        'spaceless': ['endspaceless'],
        'block': ['endblock'],
        'comment': ['endcomment'],

        # i18n
        'blocktrans': ['endblocktrans'],

        # cache
        'cache': ['endcache'],
        }

class DjangoTemplate(Template):
    registered_template = None

    def __init__(self, template_string, origin=None, name='<Unknown Template>'):
        self.theme_name, self.template_name = name.split(':')
        self.registered_template = get_registered_template(self.template_name, {})
        force_themes_tags = False

        # Treat the values for tags 'extends', 'include' and 'theme_static_file'.
        for full, tag, value in EXP_TAGS.findall(template_string):
            if ':' not in value:
                new_value = full.replace('"'+value+'"', '"%s:%s"'%(self.theme_name, value))
                template_string = template_string.replace(full, new_value)

                if tag == 'theme_static_file':
                    force_themes_tags = True

        # Forces {% load themes_tag %} if any of its tags are used but there is not loading
        if force_themes_tags and not EXP_THEME_TAG.findall(template_string):
            # The following 2 lines ensures the {% load %} comes after an {% extends %} tag
            f = EXP_EXTENDS.findall(template_string)
            pos = (template_string.index(f[0]) + len(f[0])) if f else 0
            template_string = template_string[:pos] + '{% load themes_tags %}' + template_string[pos:]

        self.check_allowed_template(template_string)

        super(DjangoTemplate, self).__init__(template_string, origin, name)

    def check_allowed_template(self, template_string):
        # Blocks unavailable loads (template tags libraries)
        available_loads = (self.registered_template.get('available_loads', None) or
                app_settings.AVAILABLE_LOADS or [])
        if available_loads != ALL:
            available_loads = list(available_loads)

            found = EXP_AV_LOAD.findall(template_string)
            if found:
                libs = reduce(lambda a,b: a+b, [i.strip().split() for i in found])
                diff = set(filter(bool, libs)).difference(set(filter(bool, available_loads)))
                if diff:
                    raise UnavailableLoad('The load of libraries "%s" is not available.'%'", "'.join(diff))

        # Blocks unavailable template tags
        available_tags = (self.registered_template.get('available_tags', None) or
                app_settings.AVAILABLE_TAGS or [])
        if available_tags != ALL:
            available_tags = list(available_tags)

            # Loads node lists for default tags
            for tag in available_tags:
                if DEFAULT_TAGS_NODES.get(tag, None):
                    available_tags.extend(DEFAULT_TAGS_NODES[tag])

            found = EXP_AV_TAG.findall(template_string)
            if found:
                diff = set(filter(bool, found)).difference(set(filter(bool, available_tags)))
                if diff:
                    raise UnavailableTag('The template tags "%s" are not available.'%'", "'.join(diff))

        # Blocks unavailable template filters
        available_filters = (self.registered_template.get('available_filters', None) or
                app_settings.AVAILABLE_FILTERS or [])
        if available_filters != ALL:
            available_filters = list(available_filters)

            found = EXP_AV_FILTER.findall(template_string)
            if found:
                filters = reduce(lambda a,b: a+b, [i.strip().split('|') for i in found])
                filters = filter(bool, [f.split(':')[0] for f in filters])
                diff = set(filter(bool, filters)).difference(set(filter(bool, available_filters)))
                if diff:
                    raise UnavailableFilter('The template filters "%s" are not available.'%'", "'.join(diff))

        # Blocks unavailable includes
        available_includes = (self.registered_template.get('available_includes', None) or
                app_settings.AVAILABLE_INCLUDES or [])
        if available_includes != ALL:
            available_includes = list(available_includes)

            found = EXP_AV_INCLUDE.findall(template_string)
            if found:
                found = [i.split(':')[-1] for i in found]
                diff = set(filter(bool, found)).difference(set(filter(bool, available_includes)))
                if diff:
                    raise UnavailableInclude('The include of template "%s" is not available.'%'", "'.join(diff))

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
    

