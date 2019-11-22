from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=15)
    password= forms.CharField(label='Password', max_length=10,widget=forms.PasswordInput)

    def __init__(self,*args, **kwargs):
    	super().__init__(*args, **kwargs)
    	self.fields['username'].widget.attrs.update({'autofocus': 'autofocus',
    		'required': 'required', 'placeholder': 'User Name'})
    	self.fields['password'].widget.attrs.update({
    		'required':'required','placeholder': 'Password'})