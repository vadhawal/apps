from django.db import models
from django.contrib.comments.signals import comment_was_posted
from django.contrib.auth.models import User
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment
from imagestore.models import Album, Image
from userProfile.models import UserWishRadio

from actstream import action, actions
from follow.models import Follow

def comment_action(sender, comment=None, target=None, **kwargs):
    if comment.user:
        if isinstance(comment.content_object, BlogPost):
            action.send(comment.user, verb=u'has posted a review on', action_object=comment, 
                target=comment.content_object)
            Follow.objects.get_or_create(comment.user, comment)
            actions.follow(comment.user, comment, send_action=False, actor_only=False) 
        elif isinstance(comment.content_object, ThreadedComment):
        	action.send(comment.user, verb=u'has commented on review', action_object=comment, 
            	target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, Album):
        	action.send(comment.user, verb=u'has commented on the album', action_object=comment, 
            	target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, Image):
            action.send(comment.user, verb=u'has commented on the image', action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, UserWishRadio):
            obj = comment.content_object
            owner = obj.content_type.get_object_for_this_type(pk=obj.object_id)
            if isinstance(owner, BlogPost):
                action.send(comment.user, verb=u'has commented on the deal', action_object=comment, 
                    target=comment.content_object, batch_time_minutes=30, is_batchable=True)
            elif isinstance(owner, User):
                action.send(comment.user, verb=u'has commented on the wish', action_object=comment, 
                    target=comment.content_object, batch_time_minutes=30, is_batchable=True)
            else:
                """
                Do Nothing
                """
            Follow.objects.get_or_create(comment.user, comment.content_object)
            actions.follow(comment.user, comment.content_object, send_action=False, actor_only=False) 

comment_was_posted.connect(comment_action)