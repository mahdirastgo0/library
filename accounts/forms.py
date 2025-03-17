from django import forms
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox




# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(
#         required=True,
#         label="ایمیل",
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'لطفا ایمیل خود را وارد کنید',
#             'required': 'required',
#             'data-validation-required-message': 'لطفا ایمیل خود را وارد کنید'
#         })
#     )
#
#     fullname = forms.CharField(
#         required=True,
#         label="نام و نام خانوادگی",
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'لطفا نام و نام خانوادگی خود را وارد کنید',
#             'required': 'required'
#         })
#     )
#
#     password1 = forms.CharField(
#         required=True,
#         label="رمز عبور",
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'لطفا رمز عبور خود را وارد کنید',
#             'required': 'required'
#         })
#     )
#
#     password2 = forms.CharField(
#         required=True,
#         label="تکرار رمز عبور",
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'لطفا رمز عبور خود را دوباره وارد کنید',
#             'required': 'required'
#         })
#     )

    # class Meta:
    #     model = User
    #     fields = ("email", "fullname", "password1", "password2")

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری خود را وارد کنید'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور را وارد کنید'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تکرار رمز عبور'})
    )

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")


    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # استفاده از ایمیل به‌عنوان یوزرنیم
        user.first_name = self.cleaned_data["fullname"]  # ذخیره نام در `first_name`
        user.is_active = False  # کاربر تا تأیید ایمیل غیرفعال می‌ماند
        if commit:
            user.save()
        return user


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")


        # Ensure at least one of email or phone is provided
        if not email :
            raise ValidationError("ایمیل معتبر نیست.")

        return cleaned_data


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور مطابقت ندارند.")
        return password2

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class UserChangeForm(forms.ModelForm):
    email = forms.EmailField()
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', "password", "is_active", "is_admin","status"]


class UserloginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def __init__(self, *args, **kwargs):
        # دریافت آرگومان `request` از kwargs و حذف آن
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


class EmailAdminLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )


