from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Blog(models.Model):
    blog_title = models.CharField(max_length=150)
    blog_content = models.TextField()
    blog_author = models.ForeignKey(User)
    blog_date_created = models.CharField(max_length=60)
    blog_timezone_date_created = models.DateTimeField(default=timezone.now)
    blog_time_since_post_creation = models.CharField(max_length=30, default='')
    blog_date_modified = models.CharField(max_length=60)
    blog_timezone_date_modified = models.DateTimeField(default=timezone.now)
    blog_time_since_post = models.CharField(max_length=30, default='')

    class Meta:
        db_table = "blog"


class UserExtraFeatures(models.Model):
    """
        this class will store when the user wrote or modified a post.
        this class will also hold a field that allows a user from posting.
    """
    blog_user = models.OneToOneField(User, primary_key=True)
    blog_last_posted_time = models.DateTimeField()
    user_can_post = models.BooleanField()

    class Meta:
        db_table = "user_extra_features"


