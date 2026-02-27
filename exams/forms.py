from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Subject


class CustomUserCreationForm(UserCreationForm):
    """Kengaytirilgan ro'yxatdan o'tish formasi"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email manzil'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ism'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiya'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Bootstrap classlarini qo'shish
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Foydalanuvchi nomi'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni takrorlang'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Profil tahrirlash formasi"""
    
    class Meta:
        model = UserProfile
        fields = ['selected_subject', 'phone_number', 'birth_date', 'school']
        widgets = {
            'selected_subject': forms.Select(attrs={
                'class': 'form-control',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 90 123 45 67'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maktab nomi'
            }),
        }
        labels = {
            'selected_subject': 'Test yo\'nalishi',
            'phone_number': 'Telefon raqam',
            'birth_date': 'Tug\'ilgan kun',
            'school': 'Maktab'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat faol yo'nalishlarni ko'rsatish
        self.fields['selected_subject'].queryset = Subject.objects.filter(is_active=True)
        self.fields['selected_subject'].required = True


class LoginForm(forms.Form):
    """Login formasi"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Foydalanuvchi nomi',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parol',
            'required': True
        })
    )