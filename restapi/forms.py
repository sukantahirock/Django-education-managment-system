from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,Course

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user




class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role']  # Add fields you want to allow editing

    def clean_username(self):
        username = self.cleaned_data['username']
        user_id = self.instance.id
        if User.objects.exclude(id=user_id).filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username



class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']