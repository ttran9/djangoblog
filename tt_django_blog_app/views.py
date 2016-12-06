from django.shortcuts import render
from django.contrib.auth.models import User
from tt_django_blog_app.models import Blog, UserExtraFeatures
from tt_django_blog_app.forms import AddForm, EditForm, LoginForm, RegistrationForm, ProcessPasswordChange
from tt_django_blog_app.utils import TimeUtility, PasswordUtility, EmailUtility, CheckForUserUtility
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from django.http import HttpResponse
import json


# Create your views here.
def show_posts(request, message=None):
    blog_posts = Blog.objects.filter().order_by('-blog_timezone_date_modified')
    current_time = timezone.now()
    current_time_formatted = TimeUtility.format_post_time(2)
    for posts in blog_posts:
        posts.blog_time_since_post = TimeUtility.check_since_posted(posts.blog_timezone_date_modified, current_time)
        posts.blog_time_since_post_creation = TimeUtility.check_since_posted(posts.blog_timezone_date_created,
                                                                             current_time)
    return render(request, "showPosts.html", {"posts": blog_posts, "time": current_time_formatted, "message": message})


def show_single_post(request, message=None):
    blog_id = request.GET.get('post_id')
    if blog_id is not None:
        single_post = Blog.objects.get(pk=blog_id)
        current_time = timezone.now()
        current_time_formatted = TimeUtility.format_post_time(2)
        single_post.blog_time_since_post = TimeUtility.check_since_posted(single_post.blog_timezone_date_modified,
                                                                          current_time)
        single_post.blog_time_since_post_creation = TimeUtility.check_since_posted(
                                                            single_post.blog_timezone_date_created, current_time)
        if message is None:
            return render(request, "singlePost.html", {"post": single_post, "time": current_time_formatted})
        else:
            return render(request, "singlePost.html", {"post": single_post, "message": message, "time":
                current_time_formatted})
    else:
        message = "you must use the parameter name, 'blog_id', to look up a single blog post."
        return render(request, "singlePost.html", {"message": message})


def show_single_post_from_post_request(request, post_id, message=None):
    """
        since this comes from the post request, it is assumed we are working with an existing blog post
        so the get should not have any errors.
    """
    single_post = Blog.objects.get(pk=post_id)
    current_time = timezone.now()
    current_time_formatted = TimeUtility.format_post_time(2)
    single_post.blog_time_since_post = TimeUtility.check_since_posted(single_post.blog_timezone_date_modified,
                                                                      current_time)
    single_post.blog_time_since_post_creation = TimeUtility.check_since_posted(
                                                            single_post.blog_timezone_date_created, current_time)
    return render(request, "singlePost.html", {"post": single_post, "message": message, "time": current_time_formatted})


def show_add_post(request):
    # check if user is logged in first.
    user_object = User.objects.get(username=str(request.user.username))
    if request.user.is_authenticated() and user_object.is_active is True:
        return render(request, "addPost.html")
    else:
        error_message = "you must be logged in before adding a post."
        return show_login(request, error_message)


def add_post(request):
    # processes adding the post
    user_object = User.objects.get(username=str(request.user.username))
    if request.user.is_authenticated() and user_object.is_active is True:
        if request.method == "POST":
            try:
                user_object_extra_features = UserExtraFeatures.objects.get(blog_user=user_object)
                last_posted_date = user_object_extra_features.blog_last_posted_time
                check_last_posted_date = TimeUtility.check_if_user_can_post(last_posted_date)
                if check_last_posted_date:
                    return help_add_post(request, user_object_extra_features)
                else:
                    message = "You must wait at least 30 seconds in between making or editing posts!"
                    return show_posts(request, message)
            except UserExtraFeatures.DoesNotExist:
                return help_add_post(request, None)
        else:
            message = "unable to add post!"
            return show_posts(request, message)
    else:
        error_message = "you must be logged in"
        return show_login(request, error_message)


def help_add_post(request, user_object_extra_features):
    add_form = AddForm(request.POST)
    if add_form.is_valid():
        if user_object_extra_features is None:
            user_object_extra_features = UserExtraFeatures()
            user_object_extra_features.blog_user = request.user
            user_object_extra_features.user_can_post = True
        blog_post = Blog()
        blog_post.blog_content = add_form.cleaned_data.get("blogContent")
        blog_post.blog_title = add_form.cleaned_data.get("blogTitle")
        blog_post.blog_author = request.user
        created_time = TimeUtility.format_post_time()
        blog_post.blog_date_created = created_time
        blog_post.blog_date_modified = created_time
        timezone_posted_time = timezone.now()
        blog_post.blog_timezone_date_modified = timezone_posted_time
        blog_post.blog_timezone_date_created = timezone_posted_time
        user_object_extra_features.blog_last_posted_time = timezone_posted_time
        try:
            blog_post.save()
            user_object_extra_features.save()
            message = "successfully added post!"
            return show_posts(request, message)
        except IntegrityError:
            message = "post was not added!"
            return show_posts(request, message)
    else:
        message = "post could not be added!"
        return show_posts(request, message)


def delete_post(request):
    user_object = User.objects.get(username=str(request.user.username))
    if request.user.is_authenticated() and user_object.is_active is True:
        if request.user.username is not None:
            current_user_name = str(request.user.username)
            post_id = request.GET.get('post_id')
            if post_id is not None:
                blog_post = Blog.objects.get(pk=post_id)
                if current_user_name == blog_post.blog_author.username:
                    try:
                        blog_post.delete()
                    except AssertionError:
                        message = "Post could not be deleted."
                        return show_posts(request, message)
                    message = "Post successfully deleted"
                    return show_posts(request, message)
            else:
                message = "You must provide a parameter with the name 'post_id' to delete a single blog post."
                return show_posts(request, message)
    else:
        message = "Must be logged in to delete a post!"
        return show_posts(request, message)


def edit_post(request):
    # show the edit post page
    user_object = User.objects.get(username=str(request.user.username))
    if request.user.is_authenticated() and user_object.is_active is True:
        # grab the post to be edited.
        post_id = request.GET.get('post_id')
        if post_id is not None:
            post = Blog.objects.get(pk=post_id)
            if post.blog_author.username == str(request.user.username):
                return render(request, "editPost.html", {"post": post})
            else:
                message = "you are not the author of this post so you cannot edit it."
                return show_single_post(request, message)
        else:
            message = "You must provide a parameter with the name 'post_id' to edit a single blog post."
            return show_posts(request, message)
    else:
        message = "Must be logged in to edit a post!"
        return show_posts(request, message)


def process_edit_post(request):
    user_object = User.objects.get(username=str(request.user.username))
    if request.user.is_authenticated() and user_object.is_active is True:
        if request.method == 'POST':
            post_form = EditForm(request.POST)
            if post_form.is_valid():
                post_id = post_form.cleaned_data.get("post_id")
                post = Blog.objects.get(pk=post_id)
                modified_post_content = post_form.cleaned_data.get("blogContent")
                original_post_content = post.blog_content
                user_object_extra_features = UserExtraFeatures.objects.get(blog_user=user_object)
                last_posted_date = user_object_extra_features.blog_last_posted_time
                if TimeUtility.check_if_user_can_post(last_posted_date):
                    if modified_post_content != original_post_content:
                        post.blog_content = modified_post_content
                        utility_object = TimeUtility()
                        post.blog_date_modified = utility_object.format_post_time()
                        timezone_posted_time = timezone.now()
                        post.blog_timezone_date_modified = timezone_posted_time
                        user_object_extra_features.blog_last_posted_time = timezone_posted_time
                        user_object_extra_features.save()
                        post.save()
                        message = "Post has been modified!"
                        return show_single_post_from_post_request(request, post_id, message)
                    else:
                        message = "No change could be made."
                        return show_single_post_from_post_request(request, post_id, message)
                else:
                    message = "You must wait 30 seconds in between creating and/or editing a post."
                    return show_single_post_from_post_request(request, post_id, message)
            else:
                message = "Your changes could not be processed."
                return show_posts(request, message)
        else:
            message = "You must submit your changes through the edit form!"
            return show_posts(request, message)
    else:
        message = "Must be logged in to edit a post!"
        return show_posts(request, message)


def show_login(request, message=None):
    if message is None:
        return render(request, "login.html")
    else:
        return render(request, "login.html", {"message": message})


def process_login(request):
    # handles user login
    # https://pypi.python.org/pypi/argon2_cffi (may not need)
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            entered_user_name = login_form.cleaned_data.get("login_userName")
            entered_password = login_form.cleaned_data.get("login_userPassword")
            user = authenticate(username=entered_user_name, password=entered_password)
            if user is not None:
                login(request, user)
                message = "You are now logged in."
                return show_posts(request, message)
    error = "could not log in!"
    return show_login(request, error)


def process_logout(request, message=None):
    logout(request)
    if message is None:
        message = "logged out!"
    return show_posts(request, message)


def show_registration(request, message=None):
    # shows the registration page
    if message is None:
        return render(request, "register.html")
    else:
        return render(request, "register.html", {"message": message})


def register_user(request):
    """
        handles when a user attempts to register with an email and a username.
        checks to see if the username is unique and if so will generate a random password.
    """
    if request.method == "POST":
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            user_name = registration_form.cleaned_data.get("register_userName")
            user_email = registration_form.cleaned_data.get("register_userEmailAddress")
            user_object_test = CheckForUserUtility.check_for_user(user_name)
            if user_object_test is None:
                generated_password = PasswordUtility.generate_password()
                try:
                    user_object = User.objects.create_user(username=user_name, email=user_email,
                                                           password=generated_password)
                    if user_object is not None:
                        # send the email
                        email_utility = EmailUtility()
                        sent_message = email_utility.send_email(user_name, user_email, generated_password)
                        if sent_message is not None:
                            message = "User successfully created, check your email to activate your account."
                            return show_login(request, message)
                        else:
                            message = "User could not be created."
                            return show_login(request, message)
                    else:
                        message = "Not able to create user, perhaps try a different username."
                        return show_registration(request, message)
                except IntegrityError:
                    message = "User name is already taken."
                    return show_registration(request, message)
            else:
                message = "User name is already taken."
                return show_registration(request, message)
        else: # slightly different message for easier debugging.
            message = "User could not be created."
            return show_registration(request, message)
    else:
        message = "You must fill out the following form to register as a user."
        return show_registration(request, message)


def show_change_password(request, message=None):
    if request.user.is_authenticated():
        if message is None:
            return render(request, "change_password.html")
        else:
            return render(request, "change_password.html", {"message": message})
    else:
        message = "Login before activating your account!"
        return show_login(request, message)


def change_password(request):
    if request.user.is_authenticated():
        activate_account_change_password_form = ProcessPasswordChange(request.POST)
        if activate_account_change_password_form.is_valid():
            user_current_password = activate_account_change_password_form.cleaned_data.get("old_password")
            user_object = CheckForUserUtility.check_for_user(str(request.user.username))
            if user_object is not None:
                if user_object.check_password(user_current_password):
                    new_password = activate_account_change_password_form.cleaned_data.get("user_password")
                    new_password_verify = activate_account_change_password_form.cleaned_data.get("user_password_verify")
                    if new_password == new_password_verify:
                        if PasswordUtility.password_checker(new_password) is not None:
                            user_object.set_password(new_password)
                            user_object.is_active = True
                            user_object.save()
                            message = "Your password has been changed! Now try to log in with the new password."
                            return process_logout(request, message)
                        else:
                            message = "Your password must have one lower and upper case letter, " \
                                      "a number, and a special character: @, #, $, %" + "<br/>" + \
                                      "The length must be between 6 and 20 characters!"
                            return show_change_password(request, message)
                    else:
                        message = "Your passwords do not match."
                        return show_change_password(request, message)
                else:
                    message = "Incorrect password, check your email for your generated password."
                    return show_change_password(request, message)
            else:
                message = "You are not the authorized user so you cannot activate this account."
                return show_login(request, message)
        else:
            message = "Be sure all fields are filled out."
            return show_change_password(request, message)
    else:
        message = "Login before activating your account!"
        return show_login(request, message)


def check_if_user_name_taken(request):
    response_dict = {"is_disabled": True}
    if request.is_ajax() and request.POST.has_key('entered_user_name'):
        entered_user_name = request.POST['entered_user_name']
        username_incorrect_format = "userName must be 6 to 35 characters, and must only have lower " \
                                    "case letters numbers, the two characters, '-' and '_'!"
        try:
            User.objects.get(username=entered_user_name)
            response_dict['server_message'] = "user name is already taken"
        except User.DoesNotExist:
            check_username_format = CheckForUserUtility.check_username_format(entered_user_name)
            if check_username_format is not None:  # user name is properly formatted and not taken.
                response_dict["is_disabled"] = False
                response_dict['server_message'] = ""
            else:  # user name has the incorrect format.
                response_dict["server_message"] = username_incorrect_format
    return HttpResponse(json.dumps(response_dict), content_type='application/json')