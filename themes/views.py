from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

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

@csrf_exempt
def theme_up_file(request, name):
    theme = get_object_or_404(Theme, name=name)
    new_static_files = []

    if request.method == 'POST':
        for up_file in request.FILES.getlist('dragupload[]'):
            name = up_file.name
            while theme.static_files.filter(name=name).count():
                name += '_'

            st = ThemeStaticFile()
            st.theme = theme
            st.name = name
            st.file = up_file
            st.save()

            new_static_files.append(st)

    return render_to_response(
            'themes/theme_up_file.html',
            {'theme': theme, 'new_static_files': new_static_files},
            context_instance=RequestContext(request),
            )

