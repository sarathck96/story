from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import F
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.views import View
from django.core.mail import EmailMessage
from django.views.generic.edit import FormView

from .forms import UserRegistrationform, StoryAddForm, AddBlog, PhotoForm, MultiUploadForm, AddCommentForm,EditProfileForm
from django.forms import ValidationError, forms
from django.contrib.auth.models import User
from .models import Story, Blog, Images, Sayoneuser, Like, Comments
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count


# Create your views here.

def home(request):
    # Loads the home page of the application sayone stories
    top_events = Story.objects.filter(story_type=0).order_by('-story_likes')[:3]
    top_blogs = Story.objects.filter(story_type=1).order_by('-story_likes')[:3]
    top_gallery = Story.objects.filter(story_type=2).order_by('-story_likes')[:3]

    context = {'events':top_events,'blogs':top_blogs,'gallery':top_gallery}
    return render(request, 'sayonestories/home.html',context )


def userregisterform(request):
    # loads the form for the user to register by entering details
    form = UserRegistrationform()
    return render(request, 'sayonestories/userregistration.html', context={'form': form})


def validate_register(request):
    """ this view validates the fields of the userregistration form and informs the user whether he/she have missed
    to enter data in a field or the data entered in the field is wrong. if all data entered is correct performs user
    registration  """
    if request.method == 'POST':
        form = UserRegistrationform(request.POST, request.FILES)
        if form.is_valid():
            sayone = form.save(commit=False)
            userObj = form.cleaned_data
            username = userObj['username']
            email = userObj['mailid']
            password = userObj['password']
            cnf_password = userObj['cnf_pass']
            name = userObj['name']

            error_codes = []
            if User.objects.filter(email=email).exists():
                error_codes.append('email_exists')
            elif User.objects.filter(username=username).exists():
                error_codes.append('username_exists')
            elif password != cnf_password:
                error_codes.append('passwords_nomatch')

            print("///", error_codes)

            if 'email_exists' in error_codes:
                form.errors['mailid'] = form.error_class(['Mail ID already in use'])

            elif 'username_exists' in error_codes:
                form.errors['username'] = form.error_class(['username already taken'])
            elif 'passwords_nomatch' in error_codes:
                form.errors['password'] = form.error_class(['passwords did not match'])

            if len(error_codes) == 0:
                sayoneuser = User.objects.create_user(first_name =name, username=username, email=email, password=password)
                sayone.user = sayoneuser
                sayone.save()
                return redirect('home')
            else:
                return render(request, 'sayonestories/userregistration.html', context={'form': form})



    else:
        form = UserRegistrationform()

    return render(request, 'sayonestories/userregistration.html', {'form': form})


def User_home_page(request):
    """loads the  Home page for specific user"""

    pic_url = request.user.sayone_user.profile_pic
  

    all_story_objects = Story.objects.all().order_by('-date_created').filter(story_status=1)

  




    return render(request, 'sayonestories/UserHome.html', context={'img_url': pic_url, 'stories': all_story_objects})


def add_story_page(request):
    """loads the page containing form to add story """

    form = StoryAddForm()

    return render(request, 'sayonestories/addstory.html', context={'form': form})


def add_story(request):
    """ adds the story enterd by the user to the database """
    if request.method == 'POST':
        form = StoryAddForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            print('/////', request.user)
            profile.story_user = request.user
            profile.story_author = request.user.sayone_user.name

            profile.save()
            return redirect('add_sub_story')
        else:
            return render(request, 'sayonestories/addstory.html', context={'form': form})
    else:
        
        render(request, 'sayonestories/addstory.html', context={'form': form})


def add_sub_story(request):
    """ substory is the story type (it could be Event,Blog,image gallery) . user is shown different forms depending on
     the story type . this view adds the substory to the database """

    story_object = Story.objects.latest('story_id')

    if story_object.story_type in [0, 1]:
        form1 = AddBlog()
        return render(request, 'sayonestories/addstory.html', context={'story': story_object, 'form1': form1})
    else:
        form2 = MultiUploadForm()
        return render(request, 'sayonestories/addstory.html', context={'story': story_object, 'form2': form2})


def add_blog(request):
    """ if the story type is blog or event then this view adds the blog/event to the database """
    print('call here')
    story_id = request.POST.get('storyid')
    story_obj = Story.objects.filter(story_id=story_id)
    print('ssss', story_obj)

    if request.method == 'POST':
        form = AddBlog(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.story = story_obj[0]
            blog.save()
            return redirect('user_home_page')
        else:
            return render(request, 'sayonestories/addstory.html', context={'form1':form})
    else:
        return render(request, 'sayonestories/addstory.html', context={})


def user_stories_page(request):
    # loads the page containing all stories added by the specific user
    story_objects_for_user = Story.objects.filter(story_user=request.user).filter(story_status=1)
    return render(request, 'sayonestories/userstories_page.html', context={'stories': story_objects_for_user})


def story_detail_page(request, id):
    """loads all the details regarding the selected story .details include story title,author,date created and
    substory details .if substory is blog or event the details include title,image and description .if substory is
    image gallery details include title and images """

    story_obj = Story.objects.filter(story_id=id)[0]

    form = AddCommentForm()
    comments = Comments.objects.filter(story_commented=story_obj)

    already_liked = ''
    if Like.objects.filter(user_liked=request.user).filter(story_liked=story_obj):
        already_liked = 'yes'
    else:
        already_liked = 'no'

    if story_obj.story_type in [0, 1]:

        context = {'blog': 'blog', 'story': story_obj,
                   'liked': already_liked, 'form': form, 'comments': comments}
        return render(request, 'sayonestories/story_detail_page.html', context)
    else:
        sub_story_object = story_obj.image_story.all()
        print(sub_story_object)

       

        for item in sub_story_object:
            print(item.file)
        context1 = {'substory': sub_story_object, 'story': story_obj, 'liked': already_liked, 'form': form,
                    'comments': comments}
        return render(request, 'sayonestories/story_detail_page.html', context=context1)


def delete_story(request, story_id):
    """ deletes the selected story and generate alert box to tell user that story has been deleted """
    item = Story.objects.get(story_id=story_id)
    item.delete()
    messages.success(request, ("Story has been deleted"))
    return redirect(user_stories_page)


def user_profile_page(request):
    """ shows the details of the user's profile .details include name,username,email ,profile pic and number of
    stories added by user. """

    profile_details = {}
    name = request.user.sayone_user.name
    mailid = request.user.sayone_user.mailid
    username = request.user.sayone_user.username
    profile_pic = request.user.sayone_user.profile_pic

    stories = Story.objects.filter(story_user=request.user)
    story_count = stories.count()

    profile_details = {'name': name, 'mailid': mailid, 'username': username, 'profile_pic': profile_pic,
                       'story_count': story_count}

    print('kkk', profile_details)
    return render(request, 'sayonestories/UserProfile.html', context={'profile_details': profile_details})


def update_profile_pic(request):
    """ allows the user to update the profile picture """

    print('test', request.FILES['pic'])
    obj = Sayoneuser.objects.get(user=request.user)
    obj.profile_pic = request.FILES['pic']
    obj.save()
    return redirect(user_profile_page)


def like_story(request, story_id):
    """ allows the user to like a story .checks whether the user have already liked the story .if already liked alerts
     the user that story is liked ,else increments the like count by one. story_id is unique id of story used to check
     whether user have already liked the story """

    story = Story.objects.get(story_id=story_id)
    can_like = ''
    if Like.objects.filter(user_liked=request.user).filter(story_liked=story):
        can_like = 'no'
    else:
        Story.objects.filter(story_id=story_id).update(story_likes=F('story_likes') + 1)
        like = Like.objects.create(user_liked=request.user, story_liked=story)
        can_like = 'yes'

    data = {'is_valid': can_like}
    return JsonResponse(data)


def add_multiple_pics(request, story_id):
    """ This view helps the user to load image gallery as part of his/her story . story_id is the unique id of the story
    that has been passed . story_id is used to fetch story object and map story and images in the database """

    story_id = story_id
    story_obj = Story.objects.filter(story_id=story_id)
    if request.method == 'POST':

        form = MultiUploadForm(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['file']:
                print('lll', each)
                Images.objects.create(file=each, story=story_obj[0])

        return redirect('user_home_page')
    else:
        form = MultiUploadForm()
        return render(request, 'sayonestories/addstory.html', context={'form2': form})


def add_comment(request, story_id):
    print('call here')
    story_id = story_id
    story_obj = Story.objects.filter(story_id=story_id)
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user_commented = request.user
            comment.story_commented = story_obj[0]
            comment.save()
            return redirect('story_detail_page', id=story_id)

    else:
        form = AddCommentForm()
        return redirect('story_detail_page', id=story_id)


def draft_stories(request):
    story_objects = Story.objects.filter(story_user=request.user).filter(story_status=0)
    return render(request, 'sayonestories/draft_stories_page.html', context={'stories': story_objects})


def draft_detail_page(request, id):
    story_object = Story.objects.get(story_id=id)
    sub_story = ''
    if story_object.story_type in [0, 1]:
        if Blog.objects.get(story=story_object):
            sub_story = 'yes'
        else:
            sub_story = 'no'
    else:
        if Images.objects.filter(story=story_object):
            sub_story = 'yes'
        else:
            sub_story = 'no'


    type = story_object.story_type

    if type in [0, 1]:
        form = AddBlog()
    else:
        form = MultiUploadForm()

    return render(request, 'sayonestories/draft_detail_page.html', context={'form': form, 'story': story_object,'sub_story':sub_story})


def publish_drafts(request):
    story_id = request.POST.get('story_id')
    story_type = request.POST.get('story_type')
    substory = request.POST.get('substory')
    story_obj = Story.objects.filter(story_id=story_id)[0]
    if substory == 'yes':
        Story.objects.filter(story_id=story_id).update(story_status=1)
        return redirect('user_home_page')

    else:
        if story_obj.story_type in [0, 1]:
            form = AddBlog(request.POST,request.FILES)
            if form.is_valid():
                blog = form.save(commit=False)
                Story.objects.filter(story_id=story_id).update(story_status=1)
                blog.story = story_obj
                blog.save()
            return redirect('user_home_page')
        else:
            form = MultiUploadForm(request.POST,request.FILES)
            if form.is_valid():
                Story.objects.filter(story_id=story_id).update(story_status=1)
                for each in form.cleaned_data['file']:
                    print('lll', each)
                    Images.objects.create(file=each, story=story_obj)
            return redirect('user_home_page')

def test(request):
    test_obj = Story.objects.get(story_id=3)
    print('ttt',test_obj.image_story.all()[0].file)

def edit_profile_page(request):

    profile_details = {}
    profile_details['name']=request.user.sayone_user.name
    profile_details['mailid']=request.user.sayone_user.mailid
    profile_details['username']=request.user.username
    profile_details['profile_pic']=request.user.sayone_user.profile_pic

    qset = Story.objects.filter(story_user=request.user)

    profile_details['stories']=len(qset)
   
    return render(request,'sayonestories/edit_profile.html',context={'profile_details':profile_details})
                     



def story_detail_page2(request,id):
    story_obj = Story.objects.filter(story_id=id)[0]
    comments = Comments.objects.filter(story_commented=story_obj)
    if story_obj.story_type in [0, 1]:

        context = {'blog': 'blog', 'story': story_obj, 'comments': comments}
        return render(request, 'sayonestories/story_detail_page2.html', context)
    else:
        sub_story_object = story_obj.image_story.all()
        print(sub_story_object)

       

        for item in sub_story_object:
            print(item.file)
        context1 = {'substory': sub_story_object, 'story': story_obj,'comments': comments}
        return render(request, 'sayonestories/story_detail_page2.html', context=context1)


def show_events(request):
    all_event_objects = Story.objects.all().order_by('-date_created').filter(story_status=1).filter(story_type=0)
    return render(request,'sayonestories/events_page.html',context={'stories':all_event_objects})

def show_blogs(request):
    all_blog_objects = Story.objects.all().order_by('-date_created').filter(story_status=1).filter(story_type=1)
    print('blogs',all_blog_objects)
    return render(request,'sayonestories/blogs_page.html',context={'stories':all_blog_objects})

def show_gallery(request):
    all_gallery_objects = Story.objects.all().order_by('-date_created').filter(story_status=1).filter(story_type=2)
    return render(request,'sayonestories/image_gallery_page.html',context={'stories':all_gallery_objects})

def top_authors(request):
    test = Story.objects.values('story_user_id').annotate(story_user_count=Count('story_user')).order_by('-story_user_count')[:2]
    top_users = []
    users_id = []
    count = []
    for item in test:
        users_id.append(item['story_user_id'])
        count.append(item['story_user_count'])
    
    for id in users_id:
        user_obj= Sayoneuser.objects.get(user=id)
        temp_dict = {}
        temp_dict['name']=user_obj.name
        temp_dict['mailid']=user_obj.mailid
        temp_dict['profile_pic']=user_obj.profile_pic
        top_users.append(temp_dict)
    
    top_users[0]['count']=count[0]
    top_users[1]['count']=count[1]
    

        
    return render(request,'sayonestories/top_authors.html',context={'authors':top_users})
            

def edit_story_page(request, id):
   story_obj = Story.objects.get(story_id=id)
   story_type = story_obj.story_type
   story_title = story_obj.story_title
 

 
   if story_type in [0, 1]:
       story_pic = story_obj.blog_story.blog_pic
       context = {'blog': 'blog', 'title': story_title, 'description': story_obj.blog_story.blog_description,
                  'pic': story_obj.blog_story.blog_pic, 'id': story_obj.story_id}
       return render(request, 'sayonestories/story_edit_page.html', context)
   else:
       for item in story_obj.image_story.all():
           print(item.id)
       context = {'title': story_title, 'id': story_obj.story_id,'story':story_obj}
       return render(request, 'sayonestories/story_edit_page.html', context)



def edit_story(request):
   story_id = request.POST.get('id')
   print('id',story_id)
   story_title = request.POST.get('title')
   story_description = request.POST.get('description')
   story_pic = request.FILES.get('newpic')

   story_obj = Story.objects.filter(story_id=story_id).first()
   story_obj.story_title = story_title
   story_obj.save()
   
   if story_obj.story_type in [0,1]:
      blog_obj = Blog.objects.filter(story=story_obj).first()
      blog_obj.blog_description = story_description
      blog_obj.blog_pic = story_pic
      blog_obj.save()
      return redirect('story_detail_page', id=story_id)
   else:
        return redirect('story_detail_page', id=story_id)