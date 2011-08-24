import os
import mimetypes

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import simplejson
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from models import Theme, ThemeTemplate, ThemeStaticFile

def home(request):
    themes = Theme.objects.order_by('verbose_name')

    if request.POST.get('name', None):
        verbose_name = request.POST['name']
        name = slugify(request.POST['name'])
        counter = 0
        while Theme.objects.filter(name=name).count():
            counter += 1
            name = '%s-%s'%(slugify(request.POST['name']), counter)
        theme = Theme.objects.create(name=name, verbose_name=verbose_name)

        messages.warning(request, _('New theme "%s" created.'))
        return HttpResponseRedirect(reverse('themes_theme', args=(theme.name,)))

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

def theme_delete(request, name):
    theme = get_object_or_404(Theme, name=name)
    theme.delete()
    messages.info(request, _('Theme "%s" deleted.')%name)
    return HttpResponseRedirect(reverse('themes_home'))

@csrf_exempt
def theme_up_file(request, name):
    theme = get_object_or_404(Theme, name=name)
    new_static_files = []

    if request.method == 'POST':
        for up_file in request.FILES.getlist('dragupload[]'):
            name = up_file.name
            while theme.static_files.filter(name=name).count():
                name += '_'

            sf = ThemeStaticFile()
            sf.theme = theme
            sf.name = name
            sf.file = up_file
            sf.mime_type = up_file.content_type
            sf.save()

            new_static_files.append(sf)

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
        elif typ in ('static-file', 'static-url'):
            item = theme.static_files.get(pk=pk)
            ext = os.path.splitext(item.file.name)[-1][1:]

            if item.mime_type.startswith('text/'):
                try:
                    content = u'type(%s)%s'%(ext, item.file.read().decode('utf-8'))
                    return HttpResponse(content)
                except ValueError:
                    pass

            try:
                url = item.get_url()
            except ValueError:
                url = item.url

            ret = {'type':item.get_type(), 'url':url, 'mime_type':item.mime_type}
            return HttpResponse(simplejson.dumps(ret)) #, mime_type='text/javascript')

@csrf_exempt
def theme_delete_child(request, name):
    theme = get_object_or_404(Theme, name=name)
    ret = {'result':'ok'}

    if request.method == 'POST':
        if request.POST['type'] == 'template':
            item = theme.templates.get(name=request.POST['name'])
            ret['info'] = {'pk':item.pk, 'name':item.name, 'type':'template'}
            item.delete()
        elif request.POST['type'] == 'static-file':
            item = theme.static_files.get(name=request.POST['name'])
            ret['info'] = {'pk':item.pk, 'name':item.name, 'type':'static-file'}
            item.delete()

    return HttpResponse(simplejson.dumps(ret), mimetype='text/javascript')

@csrf_exempt
def theme_create_template(request, name):
    theme = get_object_or_404(Theme, name=name)
    ret = {}

    if request.method == 'POST':
        name = request.POST['name']
        if theme.templates.filter(name=name).count():
            ret = {'result':'error', 'message':'Template already exists.'}
        else:
            tpl = theme.templates.create(name=name)
            ret = {'result':'ok', 'info':{'pk':tpl.pk}}

    return HttpResponse(simplejson.dumps(ret), mimetype='text/javascript')

@csrf_exempt
def theme_create_static_file(request, name):
    theme = get_object_or_404(Theme, name=name)
    ret = {}

    if request.method == 'POST':
        name = request.POST['name']
        if theme.static_files.filter(name=name).count():
            ret = {'result':'error', 'message':'Static File already exists.'}
        else:
            sf = theme.static_files.create(name=name)

            if request.POST.get('url', None):
                sf.url = request.POST['url']
                sf.mime_type = mimetypes.guess_type(sf.url)[0] or ''
                sf.save()
            else:
                file_name = '%s-%s-%s'%(theme.pk, sf.pk, name)
                content = ContentFile('')
                sf.file.save(file_name, content)

                sf.mime_type = mimetypes.guess_type(file_name)[0] or ''
                sf.save()
            ret = {'result':'ok', 'info':{'pk':sf.pk, 'url':sf.get_url()}}

    return HttpResponse(simplejson.dumps(ret), mimetype='text/javascript')

