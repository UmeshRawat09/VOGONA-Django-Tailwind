from django import forms
from .models import Account, UserProfile

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Your Password',
        'class' : 'border outline-none rounded p-2 hover:border-2',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Your Confirm Password',
        'class' : 'border outline-none rounded p-2 hover:border-2'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter Your First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Your Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Your Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Your Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'border outline-none rounded p-2 hover:border-2'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'border-2 rounded p-1'


class UserProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields =  ('address', 'city', 'state', 'profile_image')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field == 'profile_image':
                self.fields[field].widget.attrs['class'] = (
                    'w-full border-2 rounded text-gray-600 '
                    'file:p-1 hover:cursor-pointer '
                    'file:cursor-pointer '
                    'file:bg-gray-600 file:text-white '
                    'hover:file:bg-gray-700'
                )
            else:
                self.fields[field].widget.attrs['class'] = 'border-2 rounded p-1'