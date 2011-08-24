from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Theme, ThemeTemplate, ThemeStaticFile

def home(request):
    themes = Theme.objects.order_by('verbose_name')
    return render_to_response(
            'themes/home.html',
            {'themes': themes},
            context_instance=RequestContext(request),
            )

def theme(request, name):
    theme = get_object_or_404(Theme, name=name)
    return render_to_response(
            'themes/theme.html',
            {'theme': theme},
            context_instance=RequestContext(request),
            )

