from django.db import models
from django.contrib.comments.signals import comment_was_posted

from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment
from imagestore.models import Album, Image
from userProfile.models import UserWishRadio

from actstream import action

def comment_action(sender, comment=None, target=None, **kwargs):
    if comment.user:
    	if isinstance(comment.content_object, BlogPost):
        	action.send(comment.user, verb=u'has posted a review on', action_object=comment, 
            	target=comment.content_object)
        elif isinstance(comment.content_object, ThreadedComment):
        	action.send(comment.user, verb=u'has commented on review', action_object=comment, 
            	target=comment.content_object)
        elif isinstance(comment.content_object, Album):
        	action.send(comment.user, verb=u'has commented on the album', action_object=comment, 
            	target=comment.content_object)
        elif isinstance(comment.content_object, Image):
            action.send(comment.user, verb=u'has commented on the image', action_object=comment, 
                target=comment.content_object)
        elif isinstance(comment.content_object, UserWishRadio):
            action.send(comment.user, verb=u'has commented on the wish', action_object=comment, 
                target=comment.content_object)         
comment_was_posted.connect(comment_action)