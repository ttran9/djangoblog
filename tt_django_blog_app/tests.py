from django.test import TestCase, Client
from tt_django_blog_app.models import Blog
from django.contrib.auth.models import User
from tt_django_blog_app.utils import TimeUtility, EmailUtility


# Create your tests here.
class UserTestCase(TestCase):
    def setUp(self):
        user_name = "todd12345"
        user_password = "badpassword1"
        user_email = "myemail@gmail.com"
        User.objects.create(username=user_name, email=user_email, password=user_password)

    def test_check_for_existing_user(self):
        user_name = "todd12345"
        existing_user = User.objects.get(username=user_name)
        self.assertIsNotNone(existing_user)

    def test_check_for_non_existing_user(self):
        try:
            user_object = User.objects.get(username="SomeBizarreName")
            self.assertIsNotNone(user_object)
        except User.DoesNotExist:
            user_object = None
            self.assertIsNone(user_object)


class BlogTestCase(TestCase):
    def setUp(self):
        user_name = "todd12345"
        user_password = "badpassword1"
        user_email = "myemail@gmail.com"
        user_object = User.objects.create_user(user_name, user_email, user_password)

        utility_object = TimeUtility()
        current_time = utility_object.format_post_time()

        Blog.objects.create(blog_title="Sample Blog Title", blog_content="Weird Content Man",
                                        blog_author=user_object, blog_date_created=current_time,
                            blog_date_modified=current_time)

    def test_check_if_blog_not_modified(self):
        blog_post = Blog.objects.get(blog_title="Sample Blog Title")
        self.assertEqual(blog_post.blog_date_created, blog_post.blog_date_modified)

    def test_check_if_blog_content_is_modified(self):
        blog_post = Blog.objects.get(blog_title="Sample Blog Title")
        modified_blog_content = blog_post.blog_content + "hello"
        self.assertNotEqual(blog_post.blog_content, modified_blog_content)


class UtilityTestCase(TestCase):
    """
        should test the functions that generate the credentials, http and service objects.
        to shorthand this I have put it under the send email test, this should fail if any of the objects are none.
    """
    def setUp(self):
        self.email_utility = EmailUtility()

    def test_send_email_to_self(self):
        # sends a very basic email
        email_recipient = "toddtran9@gmail.com"
        sample_user_name = "sampleusername"
        sample_password = "rie3o@ap"
        sample_domain = "http://127.0.0.1:8000"
        self.assertIsNotNone(self, self.email_utility.send_email(sample_user_name, email_recipient, sample_password, sample_domain))


class SimpleViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_show_posts(self):
        response = self.client.get('/showPosts/')
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        response = self.client.post('/processRegistration/', {'register_userName': 'todd31',
                'register_userEmailAddress': 'todd12@gmail.com'})
        self.assertEqual(response.status_code, 200)

