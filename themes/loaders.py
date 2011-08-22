from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template
from django.conf import settings
from django.core.cache import cache

import app_settings
from registration import _registered_templates
from models import Theme, ThemeTemplate

class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        try:
            reg_template = _registered_templates[template_name]
        except KeyError:
            raise TemplateDoesNotExist('Template "%s" is not registered.'%template_name)

        active_theme = cache.get('themes:active', None)
        if not active_theme:
            try:
                theme = Theme.objects.get(is_default=True)
                cache.set('themes:active', theme.name, app_settings.CACHE_EXPIRATION)
            except Theme.DoesNotExist:
                raise TemplateDoesNotExist('There\'s no active theme.')

        try:
            # Using cache to restore/store template content
            cache_key = 'themes:%s|%s'%(active_theme, template_name)
            content = cache.get(cache_key, None, app_settings.CACHE_EXPIRATION)
            if not content:
                tpl = ThemeTemplate.objects.get(theme__is_default=True, name=template_name)
                content = tpl.content
                cache.set(cache_key, content)

            return (tpl.content, '%s/%s'%(tpl.theme.name, tpl.name))
        except ThemeTemplate.DoesNotExist:
            if reg_template.get('mirroring', None):
                return get_template(reg_template['mirroring'])

        raise TemplateDoesNotExist('Template "%s" doesn\'t exist in active theme.'%template_name)
    load_template_source.is_usable = True

