# from django import forms
# from common.models import Registration, Book_details, Reservation, Transaction_table, Fine_table, Book_specefic


# class Registrationform(forms.ModelForm):
#     class Meta:
#         model = Registration
#         fields = ['Roll_no', 'User_name', 'Password', 'Name', 'Phn_no', 'Batch']


# class Book_detailsform(forms.ModelForm):
#     class Meta:
#         model = Book_details
#         fields = [
#             'Book_name',
#             'Authors_name',
#             'ISBN',
#             'Genre',
#             'Language',
#             'No_of_copies',
#             'Available_books',
#             'Posessed'
#         ]

# class Reservationform(forms.ModelForm):
#     class Meta:
#         model = Reservation
#         fields = []

# class Transactionform(forms.ModelForm):
#     class Meta:
#         model = Transaction_table
#         fields = ['Access_no', 'Owned_by', 'Due_date']


# class Fineform(forms.ModelForm):
#     class Meta:
#         model = Fine_table
#         fields = ['Access_no', 'Owned_by', 'Amount', 'Due_date']

# class Book_speceficform(forms.ModelForm):
#     class Meta:
#         model = Book_specefic
#         fields = ['Access_no']
        

# class BookEditForm(forms.ModelForm):
#     class Meta:
#         model = Book_details
#         fields = ['Book_name', 'Authors_name','ISBN','Genre','Language']
        


# class BookCombinedForm(forms.Form):
#     # Book_details fields
#     Book_name = forms.CharField(max_length=100)
#     Authors_name = forms.CharField(max_length=100)
#     ISBN = forms.CharField(max_length=20)
#     Genre = forms.CharField(max_length=50)
#     Language = forms.CharField(max_length=50)
#     No_of_copies = forms.IntegerField(min_value=1)
#     Available_books = forms.IntegerField(min_value=0)
#     Possessed = forms.IntegerField(min_value=0)

#     # Book_specific field
#     Access_no = forms.IntegerField()   # linked to ISBN

from django import forms
from common.models import (
    Registration, Book_details, Reservation,
    Transaction_table, Fine_table, Book_specefic
)

# ---------------------------------------------------
# Reusable widget style (Tailwind)
# ---------------------------------------------------
text_style = {
    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400"
}


# ---------------------------------------------------
# 1. Registration Form
# ---------------------------------------------------
class Registrationform(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['Roll_no', 'User_name', 'Password', 'Name', 'Phn_no', 'Batch']
        widgets = {
            'Roll_no': forms.TextInput(attrs=text_style),
            'User_name': forms.TextInput(attrs=text_style),
            'Password': forms.TextInput(attrs=text_style),
            'Name': forms.TextInput(attrs=text_style),
            'Phn_no': forms.NumberInput(attrs=text_style),
            'Batch': forms.TextInput(attrs=text_style),
        }


# ---------------------------------------------------
# 2. Book Details Form
# ---------------------------------------------------
class Book_detailsform(forms.ModelForm):
    class Meta:
        model = Book_details
        fields = [
            'Book_name', 'Authors_name', 'ISBN', 'Genre',
            'Language', 'No_of_copies', 'Available_books', 'Posessed','cover'
        ]
        widgets = {
            field: forms.TextInput(attrs=text_style)
            for field in ['Book_name', 'Authors_name', 'ISBN', 'Genre', 'Language']
        }
        widgets.update({
            'No_of_copies': forms.NumberInput(attrs=text_style),
            'Available_books': forms.NumberInput(attrs=text_style),
            'Posessed': forms.NumberInput(attrs=text_style),
        })


# ---------------------------------------------------
# 3. Reservation Form (no fields used)
# ---------------------------------------------------
class Reservationform(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = []


# ---------------------------------------------------
# 4. Book Specific Form (ForeignKey as typed ISBN)
# ---------------------------------------------------
class Book_speceficform(forms.ModelForm):
    ISBN = forms.CharField(widget=forms.TextInput(attrs=text_style))

    class Meta:
        model = Book_specefic
        fields = ['Access_no', 'ISBN']
        widgets = {
            'Access_no': forms.NumberInput(attrs=text_style),
        }

    def clean_ISBN(self):
        isbn = self.cleaned_data['ISBN']
        try:
            return Book_details.objects.get(ISBN=isbn)
        except Book_details.DoesNotExist:
            raise forms.ValidationError("Invalid ISBN — book not found.")


# ---------------------------------------------------
# 5. Transaction Form (ForeignKeys typed manually)
# ---------------------------------------------------
class Transactionform(forms.ModelForm):
    Access_no = forms.CharField(widget=forms.TextInput(attrs=text_style))
    Owned_by = forms.CharField(widget=forms.TextInput(attrs=text_style))

    class Meta:
        model = Transaction_table
        fields = ['Access_no', 'Owned_by', 'Due_date']
        widgets = {
            'Due_date': forms.DateInput(attrs={"type": "date", **text_style}),
        }

    def clean_Access_no(self):
        access_no = self.cleaned_data['Access_no']
        try:
            return Book_specefic.objects.get(Access_no=access_no)
        except Book_specefic.DoesNotExist:
            raise forms.ValidationError("Invalid Access No — Not found in Book Specific table.")

    def clean_Owned_by(self):
        roll = self.cleaned_data['Owned_by']
        try:
            return Registration.objects.get(Roll_no=roll)
        except Registration.DoesNotExist:
            raise forms.ValidationError("Invalid Roll No — student not registered.")


# ---------------------------------------------------
# 6. Fine Form (ForeignKeys typed manually)
# ---------------------------------------------------
class Fineform(forms.ModelForm):
    Access_no = forms.CharField(widget=forms.TextInput(attrs=text_style))
    Owned_by = forms.CharField(widget=forms.TextInput(attrs=text_style))

    class Meta:
        model = Fine_table
        fields = ['Access_no', 'Owned_by', 'Amount', 'Due_date']
        widgets = {
            'Amount': forms.NumberInput(attrs=text_style),
            'Due_date': forms.DateInput(attrs={"type": "date", **text_style}),
        }

    def clean_Access_no(self):
        access_no = self.cleaned_data['Access_no']
        try:
            return Book_specefic.objects.get(Access_no=access_no)
        except Book_specefic.DoesNotExist:
            raise forms.ValidationError("Invalid Access No — Not found.")

    def clean_Owned_by(self):
        roll = self.cleaned_data['Owned_by']
        try:
            return Registration.objects.get(Roll_no=roll)
        except Registration.DoesNotExist:
            raise forms.ValidationError("Invalid Roll No — Not registered.")


# ---------------------------------------------------
# 7. Book Edit Form
# ---------------------------------------------------
class BookEditForm(forms.ModelForm):
    class Meta:
        model = Book_details
        fields = ['Book_name', 'Authors_name', 'ISBN', 'Genre', 'Language']
        widgets = {
            'Book_name': forms.TextInput(attrs=text_style),
            'Authors_name': forms.TextInput(attrs=text_style),
            'ISBN': forms.TextInput(attrs=text_style),
            'Genre': forms.TextInput(attrs=text_style),
            'Language': forms.TextInput(attrs=text_style),
        }


# ---------------------------------------------------
# 8. Combined Book & Access Form
# ---------------------------------------------------
class BookCombinedForm(forms.Form):
    Book_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=text_style))
    Authors_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=text_style))
    ISBN = forms.CharField(max_length=20, widget=forms.TextInput(attrs=text_style))
    Genre = forms.CharField(max_length=50, widget=forms.TextInput(attrs=text_style))
    Language = forms.CharField(max_length=50, widget=forms.TextInput(attrs=text_style))
    No_of_copies = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs=text_style))
    Available_books = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs=text_style))
    Posessed = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs=text_style))
    cover = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full','rows': 4,'placeholder': 'Enter book description'
        }),required=False)
    Access_no = forms.IntegerField(widget=forms.NumberInput(attrs=text_style))


# class BookCombinedForm(forms.Form):
#     Book_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Authors_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     ISBN = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Genre = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Language = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     No_of_copies = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Available_books = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Posessed = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     cover = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'border rounded px-3 py-2 w-full'}))
#     Access_no = forms.IntegerField(widget=forms.NumberInput(attrs=text_style))