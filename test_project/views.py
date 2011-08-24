from django.shortcuts import render_to_response
from django.template import RequestContext

from themes.registration import register_template
from themes.models import Theme

def home(request):
    return render_to_response('home', {}, context_instance=RequestContext(request))

register_template('base', mirroring='base.html')
register_template('home')
register_template('contact')
register_template('about')

def choose_theme(request):
    if request.user.is_authenticated():
        try:
            return Theme.objects.filter(is_default=False)[0]
        except IndexError:
            return None

