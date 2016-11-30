from django import forms


class AddForm(forms.Form):
    blogTitle = forms.CharField(max_length=150)
    blogContent = forms.CharField(widget=forms.Textarea)


class LoginForm(forms.Form):
    login_userName = forms.CharField(max_length=35)
    login_userPassword = forms.CharField(max_length=20)


class RegistrationForm(forms.Form):
    # this form will generate the password for a user assuming the username isn't already taken.
    register_userName = forms.CharField(max_length=35)
    register_userEmailAddress = forms.EmailField(help_text='A valid working email address please.')


class ProcessPasswordChange(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(), max_length=20)
    user_password = forms.CharField(widget=forms.PasswordInput(), max_length=20)
    user_password_verify = forms.CharField(widget=forms.PasswordInput(), max_length=20)


class EditForm(forms.Form):
    blogTitle = forms.CharField(max_length=150)
    blogContent = forms.CharField(widget=forms.Textarea)
    post_id = forms.CharField(widget=forms.HiddenInput)

