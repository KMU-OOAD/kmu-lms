from django import forms

class BookSearchForm(forms.Form):
    query = forms.CharField(
        label='검색어',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '도서명 또는 저자명 입력'})
    ) 