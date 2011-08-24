from django.contrib import admin

from models import Theme, ThemeTemplate, ThemeStaticFile

class AdminTheme(admin.ModelAdmin):
    pass
admin.site.register(Theme, AdminTheme)

class AdminThemeTemplate(admin.ModelAdmin):
    list_filters = ('theme',)
    list_display = ('name','theme',)
admin.site.register(ThemeTemplate, AdminThemeTemplate)

class AdminThemeStaticFile(admin.ModelAdmin):
    list_filters = ('theme',)
    list_display = ('name','theme',)
admin.site.register(ThemeStaticFile, AdminThemeStaticFile)

