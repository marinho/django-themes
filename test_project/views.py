from django.shortcuts import render_to_response
from django.template import RequestContext

from themes.registration import register_template

def home(request):
    return render_to_response('home', {}, context_instance=RequestContext(request))

register_template('home')

