from django.shortcuts import render_to_response
from django.template import RequestContext
from userProfile.models import BroadcastForm
from django.http import HttpResponse
from django.shortcuts import render
from actstream import action
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

def close_login_popup(request):
    return render_to_response('close_popup.html', {}, RequestContext(request))

def broadcast(request):
	if request.method == "POST":
		action.send(request.user, verb=string_concat('said', ': ', _(request.POST['message'])))
	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))