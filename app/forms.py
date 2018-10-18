from django import forms

class EmailForm(forms.Form):
    title = forms.CharField()