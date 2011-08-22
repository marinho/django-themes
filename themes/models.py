from django.db import models
from django.core.cache import cache

from registration import _registered_templates

class Theme(models.Model):
    class Meta:
        ordering = ('verbose_name','name',)

    name = models.CharField(max_length=50, unique=True)
    verbose_name = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return self.verbose_name or self.name

    def create_templates(self):
        """Creates a template instance for every registered templates."""
        for name, params in _registered_templates.items():
            self.templates.get_or_create(name=name)

class ThemeTemplate(models.Model):
    class Meta:
        unique_together = (('theme','name'),)
        ordering = ('name',)

    theme = models.ForeignKey('Theme', related_name='templates')
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    content = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class ThemeStaticFile(models.Model):
    class Meta:
        unique_together = (('theme','name'),)
        ordering = ('name',)

    theme = models.ForeignKey('Theme', related_name='static_files')
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='theme-static-files', blank=True, null=True)

    def __unicode__(self):
        return self.name

# SIGNALS
from django.db.models import signals

def theme_post_save(instance, sender, **kwargs):
    # Sets the other themes "non-default" if this instance is default.
    if instance.is_default:
        sender.objects.exclude(pk=instance.pk).update(is_default=False)
signals.post_save.connect(theme_post_save, sender=Theme)

def themetemplate_post_save(instance, sender, **kwargs):
    # Cache invalidation
    cache_key = 'themes:%s|%s'%(instance.theme.name, instance.name)
    if cache.get(cache_key):
        cache.set(cache_key, None, 1) # Expires fastly, to clear cache storage
signals.post_save.connect(themetemplate_post_save, sender=ThemeTemplate)
