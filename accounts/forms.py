from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = ['student_id', 'username', 'phone', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # 모든 필드를 명시적으로 필수(required=True)로 설정
        for field in self.fields.values():
            field.required = True


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="학번")
    password = forms.CharField(widget=forms.PasswordInput)