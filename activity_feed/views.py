from actstream.models import user_stream


def get_(request):
	return user_stream(request.user)# Create your views here.
