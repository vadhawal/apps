from django.shortcuts import render_to_response
from django.template import RequestContext
from userProfile.models import BroadcastForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from actstream import action
from django.utils.translation import ugettext_lazy as _

def close_login_popup(request):
    return render_to_response('close_popup.html', {}, RequestContext(request))

def broadcast(request):
	if request.method == "POST":
		action.send(request.user, verb=_(request.POST['message']))
	return render_to_response('broadcast_success.html', {}, RequestContext(request))