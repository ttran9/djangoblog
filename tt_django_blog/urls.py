"""DjangoBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from tt_django_blog_app import views

urlpatterns = [
    url(r'^showPosts/$', views.show_posts, name='show_posts'),
    url(r'^addPost/', views.show_add_post, name='show_add_post'),
    url(r'^processAddPost/', views.add_post, name='add_post'),
    url(r'^login/', views.show_login, name='show_login'),
    url(r'^register/', views.show_registration, name='show_registration'),
    url(r'^processRegistration/', views.register_user, name='register_user'),
    url(r'^showChangePassword/', views.show_change_password, name='show_change_password'),
    url(r'^processChangePassword/', views.change_password, name='process_change_password'),
    url(r'^showSinglePost/$', views.show_single_post, name="show_single_post"),
    url(r'^showEditPost/$', views.edit_post, name="edit_post"),
    url(r'^processEditPost/', views.process_edit_post, name="process_edit_post"),
    url(r'^logout/', views.process_logout, name='process_logout'),
    url(r'^processLogin', views.process_login, name='process_login'),
    url(r'^deletePost/$', views.delete_post, name='delete_post'),
    url(r'^$', views.show_posts, name='home'),  # simulating home link
]

