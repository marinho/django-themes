from django.template.loader import BaseLoader, make_origin, get_template
from django.template.base import TemplateDoesNotExist
from django.conf import settings
from django.core.cache import cache
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

import app_settings
from registration import _registered_templates
from models import Theme, ThemeTemplate

class Loader(BaseLoader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        if ':' in template_name:
            active_theme, template_name = template_name.split(':', 1)
        else:
            active_theme = cache.get('themes:active', None)
            if not active_theme:
                try:
                    theme = Theme.objects.get(is_default=True)
                    cache.set('themes:active', theme.name, app_settings.CACHE_EXPIRATION)
                    active_theme = theme.name
                except Theme.DoesNotExist:
                    raise TemplateDoesNotExist('There\'s no active theme.')

        try:
            reg_template = _registered_templates[template_name]
        except KeyError:
            reg_template = {}
            #raise TemplateDoesNotExist('Template "%s" is not registered.'%template_name)

        content = None
        origin = None
        engine = None
        try:
            # Using cache to restore/store template content
            cache_key = 'themes:%s|%s'%(active_theme, template_name)
            content = cache.get(cache_key, None)

            if not content:
                tpl = ThemeTemplate.objects.get(theme__name=active_theme, name=template_name)
                engine = tpl.engine
                content = tpl.content
                cache.set(cache_key, 'engine:%s;%s'%(engine,content), app_settings.CACHE_EXPIRATION)

            origin = '%s:%s'%(active_theme, template_name)
        except ThemeTemplate.DoesNotExist:
            if reg_template and reg_template.get('mirroring', None):
                content, origin = get_template(reg_template['mirroring'])

        if content is None:
            raise TemplateDoesNotExist('Template "%s" doesn\'t exist in active theme.'%template_name)

        if content.startswith('engine:'):
            engine, content = content.split(';', 1)
            engine = engine.split(':')[1]

        try:
            template_class = get_engine_class(engine or app_settings.DEFAULT_ENGINE)
            template = template_class(content, origin, template_name)

            return template, None
        except TemplateDoesNotExist:
            return content, origin


def get_engine_class(path):
    if isinstance(path, basestring):
        module, attr = path.rsplit('.', 1)

        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Template engine "%s" was not found.'%path)

        try:
            return getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Template engine "%s" was not found.'%path)


