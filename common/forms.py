
from django import forms
from django.core.validators import RegexValidator, EmailValidator
from common.models import (
    Registration, Book_details, Reservation,
    Transaction_table, Fine_table, Book_copy,Librarian,Books_online_copies
)

from django.core.exceptions import ValidationError


text_style = {
    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400"
}
class LoginForm(forms.ModelForm):
    class Meta:
        model=Registration
        fields = ['email', 'Password',]
        widgets={
            'email': forms.TextInput(attrs=text_style),
            'Password': forms.PasswordInput(attrs=text_style),
        }







class Registrationform(forms.ModelForm):

    # Custom Validators
    name_validator = RegexValidator(
        regex=r'^[A-Za-z ]+$',
        message="Name must contain only alphabets and spaces."
    )

    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )

    class Meta:
        model = Registration
        fields = ['roles','department','Roll_no', 'Password', 'Name', 'Phn_no', 'Batch', 'email']

        labels = {
            'Roll_no': 'staff id/ roll number',
            'Password': 'Password',
            'Name': 'Full Name',
            'Phn_no': 'Phone Number',
            'Batch': 'Batch',
            'email': 'Email Address',
        }

        widgets = {
            'Roll_no': forms.TextInput(attrs=text_style),
            'Password': forms.PasswordInput(attrs=text_style),
            'Name': forms.TextInput(attrs=text_style),
            'Phn_no': forms.TextInput(attrs=text_style),
            'Batch': forms.TextInput(attrs=text_style),
            'email': forms.EmailInput(attrs=text_style),

        }

    # Field-level validation
    Name = forms.CharField(
        validators=[name_validator]
    )

    Phn_no = forms.CharField(
        validators=[phone_validator]
    )

    email = forms.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")]
    )

    Password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs=text_style),
        help_text="Password must be at least 6 characters long."
    )


# ---------------------------------------------------
# 2. Book Details Form
# ---------------------------------------------------
class Book_detailsform(forms.ModelForm):
    number_of_copies = forms.IntegerField(
        min_value=1,
        label="Number of Copies",
        help_text="How many physical copies to create"
    )

    class Meta:
        model = Book_details
        fields = '__all__'   # form-only field will not be saved

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-black'
            })


class BooksOnlineForm(forms.ModelForm):

    class Meta:
        model = Books_online_copies
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-black'
            })

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
                if not file.name.endswith(".pdf"):
                    raise ValidationError("Only PDF files allowed.")
                if file.size > 20 * 1024 * 1024:
                    raise ValidationError("File size must be under 20MB.")

        return file






class LibrarianForm(forms.ModelForm):
    class Meta:
        model = Librarian
        fields = ['user_name','password']

        widgets = {
            'user_name':forms.TextInput(
                attrs=text_style
            ),
            'password':forms.PasswordInput(
                attrs=text_style
            )
        }