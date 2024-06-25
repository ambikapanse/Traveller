import uuid
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="Picture", null=True)
    location = models.CharField(max_length=100, verbose_name="Location", null=True)
    caption = models.CharField(max_length=10000000, verbose_name="Caption")
    posted = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    likes = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('post-details', args=[str(self.id)])

    def __str__(self):
        return self.caption


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")


def add_post(instance, created, **kwargs):
    if created:
        post = instance
        user = post.user
        followers = Follow.objects.filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stream_following")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stream_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()


post_save.connect(add_post, sender=Post)
