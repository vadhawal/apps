from django.db import models
from django.contrib.comments.signals import comment_was_posted

from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment

from actstream import action

def comment_action(sender, comment=None, target=None, **kwargs):
    if comment.user:
    	if isinstance(comment.content_object, BlogPost):
        	action.send(comment.user, verb=u'has posted a review on', action_object=comment, 
            	target=comment.content_object)
        elif isinstance(comment.content_object, ThreadedComment):
        	action.send(comment.user, verb=u'has commented on review', action_object=comment, 
            	target=comment.content_object)        
comment_was_posted.connect(comment_action)