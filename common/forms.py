
from django import forms
from common.models import (
    Registration, Book_details, Reservation,
    Transaction_table, Fine_table, Book_copy,Librarian
)


text_style = {
    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400"
}


# user registration form
class Registrationform(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['Roll_no', 'User_name', 'Password', 'Name', 'Phn_no', 'Batch']

        widgets = {
            'Roll_no': forms.TextInput(attrs={
                **text_style,
                
            }),
            'User_name': forms.TextInput(attrs=text_style),
            'Password': forms.PasswordInput(attrs=text_style),
            'Name': forms.TextInput(attrs=text_style),
            'Phn_no': forms.NumberInput(attrs=text_style),
            'Batch': forms.TextInput(attrs=text_style),
        }



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