import os

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse

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

@csrf_exempt
def theme_edit_child(request, name):
    theme = get_object_or_404(Theme, name=name)

    if request.method == 'POST':
        if request.POST['type'] == 'template':
            item = theme.templates.get(name=request.POST['name'])
            item.content = request.POST['content']
            item.save()
            return HttpResponse('ok')
        elif request.POST['type'] == 'static-file':
            item = theme.static_files.get(name=request.POST['name'])
            file_path = item.file.path
            fp = file(file_path, 'w')
            fp.write(request.POST['content'].encode('utf-8'))
            fp.close()
            return HttpResponse('ok')
    else:
        rel = request.GET['rel']
        typ, pk = rel.rsplit('-',1)

        if typ == 'template':
            item = theme.templates.get(pk=pk)
            return HttpResponse(u'type(html)'+item.content)
        elif typ == 'static-file':
            item = theme.static_files.get(pk=pk)
            ext = os.path.splitext(item.file.name)[-1][1:]
            return HttpResponse(u'type(%s)%s'%(ext, item.file.read().decode('utf-8')))

