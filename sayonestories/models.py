from django.db import models
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from upload_validator import FileTypeValidator
from django.contrib.auth.password_validation import validate_password



class Sayoneuser(models.Model):
    name = models.CharField(max_length=70, validators=[MinLengthValidator(5)])
    mailid = models.EmailField(max_length=70)
    username = models.CharField(max_length=70)
    password = models.CharField(max_length=30,validators=[validate_password])
    cnf_pass = models.CharField(max_length=30)
    profile_pic = models.ImageField(upload_to='images',default='images/default_pic.jpg',null=True,blank=True,
                                    validators=[FileTypeValidator(
                                        allowed_types=['image/jpeg', 'image/png']
                                    )]
                                    )
    user = models.OneToOneField(User, related_name='sayone_user', on_delete=models.CASCADE)

class Story(models.Model):
    story_type_choices = (
        (0,"Event"),
        (1,"Blog"),
        (2,"Image Gallery"),
    )

    status_choices = (
        (0,"Draft"),
        (1,"Publish"),
    )
    story_id = models.AutoField(primary_key=True)
    story_author = models.CharField(max_length=50)

    story_title = models.CharField(max_length=50)
    story_likes = models.IntegerField(default=0)
    story_type = models.IntegerField(choices=story_type_choices,default=0)
    story_status = models.IntegerField(choices=status_choices,default=0)
    
    date_created = models.DateTimeField(auto_now_add=True)
    story_user = models.ForeignKey(User,related_name='story_user',on_delete=models.CASCADE)

class Blog(models.Model):
    blog_id = models.AutoField(primary_key=True)
    blog_pic = models.ImageField(upload_to='images')
    blog_description = models.CharField(max_length=5000)
    story = models.OneToOneField(Story,on_delete=models.CASCADE,related_name='blog_story')

class Images(models.Model):
    file = models.ImageField(upload_to='images')
    story = models.ForeignKey(Story,on_delete=models.CASCADE, related_name='image_story')

class Like(models.Model):

    user_liked = models.ForeignKey(User,on_delete=models.CASCADE)
    story_liked = models.ForeignKey(Story,on_delete=models.CASCADE)

class Comments(models.Model):
   user_commented = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_comment')
   story_commented = models.ForeignKey(Story,on_delete=models.CASCADE,related_name='story_comment')
   comment = models.CharField(max_length=2000)
   date_commented = models.DateTimeField(auto_now_add=True)


class StoryView(models.Model):
    story = models.ForeignKey(Story,related_name='storyviews',on_delete=models.CASCADE)
    session= models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)


class Replies(models.Model):
    reply = models.CharField(max_length=1000)
    comment_replied = models.ForeignKey(Comments, related_name='reply_to_comment', on_delete=models.CASCADE)
    user_replied = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reply')
    user_replied_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_replied_to')
    date_replied = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Replies'

class Favourites(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_fav')
    story_added = models.ForeignKey(Story,on_delete=models.CASCADE,related_name='story_fav')

