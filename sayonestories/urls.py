from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('userregform', views.userregisterform, name='userregister'),
    path('validateregister',views.validate_register, name='validate_register'),
    path('userhome',views.User_home_page,name='user_home_page'),
    path('addstorypage',views.add_story_page,name='add_story_page'),
    path('substory',views.add_sub_story,name='add_sub_story'),
    path('addstory',views.add_story,name='add_story'),
    path('addblog',views.add_blog, name='add_blog'),
 
    path('userstorypage',views.user_stories_page,name='user_stories_page'),
    path('storydetail/<int:id>/',views.story_detail_page,name='story_detail_page'),
    path('delete_story/<int:story_id>/',views.delete_story,name='delete_story'),
    path('userprofilepage',views.user_profile_page,name='user_profile_page'),
    path('updateprofilepic',views.update_profile_pic, name='update_profile_pic'),
    path('like_story/<int:story_id>/',views.like_story, name='like_story'),


    path('multiple_pic_upload/<int:story_id>/' ,views.add_multiple_pics,name='multiple_pic_upload'),

    path('addcomment/<int:story_id>/',views.add_comment, name='add_comment'),
    path('draftstories', views.draft_stories, name='draft_stories'),
    path('draftdetail/<int:id>/',views.draft_detail_page, name='draft_detail_page'),

    path('publishdrafts',views.publish_drafts, name='publish_drafts'),
    path('testing',views.test, name='testing'),
    path('edit_profile',views.edit_profile_page, name='edit_profile'),
    path('storydetail2/<int:id>/',views.story_detail_page2, name='story_detail_page2'),
    path('showevents',views.show_events,name='show_events'),
    path('showblogs',views.show_blogs,name='show_blogs'),
    path('showgallery',views.show_gallery, name='show_gallery'),
    path('topauthors',views.top_authors,name='top_authors'),
    path('editstorypage/<int:id>/',views.edit_story_page,name='edit_story_page'),
    path('editstory',views.edit_story,name='edit_story'),
  




]
