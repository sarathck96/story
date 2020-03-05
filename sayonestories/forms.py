from django import forms
from django.core.validators import MinLengthValidator

from .models import Sayoneuser, Story, Blog, Images ,Comments
from django.core import validators
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField
from django.contrib.auth.forms import UserChangeForm

class UserRegistrationform(forms.ModelForm):
    class Meta:
        model = Sayoneuser
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mailid': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': "form-control"}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'cnf_pass': forms.PasswordInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control-file border'}),
        }
        labels = {
            'name': 'FULLNAME',
            'mailid': 'MAIL ID',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'cnf_pass': 'CONFIRM PASSWORD',
            'profile_pic': 'PROFILE PIC'
        }


class StoryAddForm(forms.ModelForm):
    class Meta:
        model = Story
        exclude = ('story_user','story_author','story_likes','story_status')

        widgets = {
            'story_title':forms.TextInput(attrs={'class':'form-control'}),
            'story_type':forms.Select(attrs={'class':'form-control'}),
            
        }

        labels = {
            'story_title': 'Story Title',
            'story_type': 'Story Type',
            

        }


class AddBlog(forms.ModelForm):
    class Meta:
        model = Blog
        exclude = ('story',)
        widgets = {
            'blog_pic': forms.FileInput(attrs={'class': 'form-control-file border'}),
            'blog_description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        labels = {
            'blog_pic': 'Add Image',
            'blog_description': 'Content'
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ('file',)

class MultiUploadForm(forms.ModelForm):

    file = MultiFileField(min_num=1, max_num=4, max_file_size=1024 * 1024 * 5)

    class Meta:
        exclude = ('story',)
        model = Images

class AddCommentForm(forms.ModelForm):

   class Meta:
       model = Comments
       exclude = ('user_commented','story_commented',)

       widgets = {
           'comment': forms.TextInput(attrs={'class':'form-control'})

       }


class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            
           
        )

 class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ("There is no user registered with the specified E-Mail address.")
            self.add_error('email', msg)
        return email


class MultiUploadForm2(forms.ModelForm):

    file = MultiFileField(min_num=1, max_num=4, max_file_size=1024 * 1024 * 5)

    class Meta:
        exclude = ('story','description')
        model = Images
    labels = {
        'file':'*Images',

        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Replies
        fields = ('reply',)

        widgets = {
            'reply': forms.Textarea(attrs={'class': 'form-control','id':'reply-text','rows':3,'cols':15})

        }
       

     
