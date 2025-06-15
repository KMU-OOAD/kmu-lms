from django import forms
from .models import LibraryInfo

class LibraryInfoForm(forms.ModelForm):
    class Meta:
        model = LibraryInfo
        fields = ['day', 'open_time', 'close_time']
