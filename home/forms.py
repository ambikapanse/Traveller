from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from dashboard.models import *
class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email address.")
        return email


class ProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea)
    location = forms.CharField(max_length=100)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location']



class PostForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.Textarea(attrs={'class':'input is-medium'}), required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=True)

    class Meta:
        model = Post
        fields = ('picture', 'caption', 'location')