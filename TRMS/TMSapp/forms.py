from fileinput import FileInput
from mailbox import Message
from django.forms.widgets import FileInput
from django import forms
from django import forms
from .models import Message
from django import forms
from .models import Driver
from .models import Profile
from .models import Message
from django.forms.models import ModelForm

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driving License/National Identification Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your Password'}))

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['username','national_id']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_image']
        exclude = ['user']
        widgets = {
            'profile_img': FileInput(),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
       
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient']