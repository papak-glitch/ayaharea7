from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


from django import forms
from django.forms.widgets import PasswordInput, TextInput

from django import forms
from django.contrib.auth.models import User
from django import forms
from .models import Event


from django import forms


from django import forms

# events/forms.py
from django import forms
from .models import Event

from django.utils import timezone

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Event date cannot be in the past.")
        return date       
    

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Your Name'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts...'
            }),
        }

class ReplyForm(CommentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = 'Write your reply...'        