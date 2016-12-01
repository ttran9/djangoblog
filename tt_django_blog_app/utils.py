import httplib2, base64, os, re
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient import discovery, errors
from email.mime.text import MIMEText
from tt_django_blog import settings
from django.contrib.auth.models import User
from django.utils import timezone
from strgen import StringGenerator
from dateutil import relativedelta as rdelta


class TimeUtility:
    @staticmethod
    def format_post_time(version=1):
        unparsed_time = timezone.now().astimezone(timezone.utc).replace(tzinfo=None)
        day_unparsed = unparsed_time.strftime("%d")
        day_unparsed = str(day_unparsed)
        hour_unparsed = int(unparsed_time.strftime("%I"))
        hour_unparsed = str(hour_unparsed)
        day_name = unparsed_time.strftime("%A") + ", "
        if version == 1:
            date_and_time = unparsed_time.strftime(day_name + "%B " + day_unparsed + ", %Y at " + hour_unparsed
                                                   + ":%M%p")
        else:
            date_and_time = unparsed_time.strftime(hour_unparsed + ":%M%p") + "\n" + unparsed_time.strftime(day_name
                                                                                    + "%B " + day_unparsed + ", %Y")
        return date_and_time

    @staticmethod
    def check_if_user_can_post(last_posted_time):
        last_posted_time = last_posted_time.astimezone(timezone.utc).replace(tzinfo=None)
        current_time = timezone.now().astimezone(timezone.utc).replace(tzinfo=None)
        seconds_since_last_post = (current_time - last_posted_time).total_seconds()
        time_allowed_inbetween_posts = 30.000  # in seconds
        if seconds_since_last_post >= time_allowed_inbetween_posts:
            return True
        else:
            return False

    @staticmethod
    def check_since_posted(last_posted_time, current_time):
        """
            this code will need to be refactored.
            :param last_posted_time: a datetime utils object to be used for comparison.
            :param current_time: this should be constant from when the user makes the request to see all the posts.
            :return: A formatted string to be displayed when the user views blog posts.
        """
        last_posted_time = last_posted_time.astimezone(timezone.utc).replace(tzinfo=None)
        current_time = current_time.astimezone(timezone.utc).replace(tzinfo=None)
        time_difference = rdelta.relativedelta(current_time, last_posted_time)
        time_since_last_post = ''
        last_post_time = []
        if time_difference.years > 0:
            last_post_time.append(str(time_difference.years) + 'y, ')
        if time_difference.months > 0:
            last_post_time.append(str(time_difference.months) + 'm, ')
        if time_difference.weeks > 0:
            last_post_time.append(str(time_difference.weeks) + 'w, ')
        if time_difference.days > 0:
            last_post_time.append(str(time_difference.days) + 'd, ')
        if time_difference.hours > 0:
            last_post_time.append(str(time_difference.hours) + 'h, ')
        if time_difference.minutes > 0:
            last_post_time.append(str(time_difference.minutes) + 'm, ')
        if time_difference.seconds > 0:
            last_post_time.append(str(time_difference.seconds) + 's')

        if len(last_post_time) > 0:
            time_since_last_post = ''.join(last_post_time)
			if len(last_post_time) == 1:
                time_since_last_post = time_since_last_post.replace(",", "")
            time_since_last_post = "%s %s" % (time_since_last_post, 'ago')

        if time_since_last_post == '':
            return None
        else:
            return time_since_last_post


class EmailUtility:
    """
        helpful link: https://gist.github.com/olgakogan/df29b5115d160e42bbd4
        the above link is to manually generate the credentials json file that can be used with the Storage object.
    """

    def __init__(self):
        self.secret_client_file = os.path.join(settings.STATIC_ROOT, 'json', 'client_secret.json')
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.scope = "https://www.googleapis.com/auth/gmail.send"
        self.flags = tools.argparser.parse_args(args=[])
        self.application_name = "python-django-blog-project"
        self.credentials_file = os.path.join(settings.STATIC_ROOT, 'json', 'django-blog-credentials.json')
        self.email_sender = "me"
        self.subject = "Django Blog Credentials"

    def get_credentials(self):
        # example taken from: https://developers.google.com/gmail/api/quickstart/python
        store = Storage(self.credentials_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = flow_from_clientsecrets(self.secret_client_file, scope=self.scope, redirect_uri=self.redirect_uri)
            flow.user_agent = self.application_name
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run_flow(flow, store)
        return credentials

    @staticmethod
    def create_http_object(credentials):
        http = credentials.authorize(httplib2.Http())
        return http

    @staticmethod
    def create_service_method(http):
        service = discovery.build('gmail', 'v1', http=http)
        return service

    @staticmethod
    def create_message(sender, to, subject, user_name, user_password):
        """Create a message for an email.
        Returns:
        An object containing a base64url encoded email object.
        """
        message_text_part_1 = "Hello, below is the following credentials for your log-in.\n"
        message_text_part_2 = "User name is: " + user_name + "\n"
        message_text_part_3 = "Password: " + user_password + "\n"
        message = MIMEText(message_text_part_1 + message_text_part_2 + message_text_part_3)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    @staticmethod
    def send_message(service, user_id, message):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print 'Message Id: %s' % message['id']
            return message
        except errors.HttpError, error:
            print 'An error occurred: %s' % error

    def send_email(self, user_name, user_email, user_generated_password):
        credentials = self.get_credentials()
        http_object = EmailUtility.create_http_object(credentials)
        service_object = discovery.build('gmail', 'v1', http=http_object)
        created_email_message = EmailUtility.create_message(self.email_sender, user_email, self.subject,
                                                            user_name, user_generated_password)
        return EmailUtility.send_message(service_object, self.email_sender, created_email_message)


class PasswordUtility:
    @staticmethod
    def password_checker(password):
        password_regex = "((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%])(?!.*\\s).{6,20})"
        pattern = re.compile(password_regex)
        return pattern.match(password)

    @staticmethod
    def generate_password():
        password_regex = '[a-z]{2:4}&[@#\$%]{1:2}&[A-Z]{2:4}&[0-9]{2:4}'
        return str(StringGenerator(password_regex).render())


class CheckForUserUtility:
    @staticmethod
    def check_for_user(username):
        try:
            user_object = User.objects.get(username=username)
            return user_object
        except User.DoesNotExist:
            return None


