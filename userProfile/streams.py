from datetime import datetime

from django.contrib.contenttypes.models import ContentType

from actstream.managers import ActionManager, stream


class FeedActionManager(ActionManager):

    @stream
    def myStreamFilterTime(self, object, time=None):
        if time is None:
            time = datetime.now()
        return object.actor_actions.filter(timestamp__lte = time)

    @stream
    def myStreamFilterVerb(self, verb):
        return self.filter(verb=verb)
