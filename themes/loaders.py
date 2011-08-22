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
            raise TemplateDoesNotExist('Template "%s" is not registered.'%template_name)

        source, display_name = self.load_template_source(active_theme, template_name)
        origin = make_origin(display_name, self.load_template_source, template_name, template_dirs)

        try:
            template_class = get_engine_class(reg_template.get('engine', None) or app_settings.DEFAULT_ENGINE)
            template = template_class(source, origin, template_name)
            return template, None
        except TemplateDoesNotExist:
            return source, display_name        

    def load_template_source(self, active_theme, template_name):
        try:
            # Using cache to restore/store template content
            cache_key = 'themes:%s|%s'%(active_theme, template_name)
            content = cache.get(cache_key, None, app_settings.CACHE_EXPIRATION)
            if not content:
                tpl = ThemeTemplate.objects.get(theme__name=active_theme, name=template_name)
                content = tpl.content
                cache.set(cache_key, content)

            return (tpl.content, '%s/%s'%(tpl.theme.name, tpl.name))
        except ThemeTemplate.DoesNotExist:
            if reg_template.get('mirroring', None):
                return get_template(reg_template['mirroring'])

        raise TemplateDoesNotExist('Template "%s" doesn\'t exist in active theme.'%template_name)
    load_template_source.is_usable = True

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


