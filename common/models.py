# from django.db import models
# from django.core.validators import MinValueValidator
# from datetime import date, timedelta
# from django.utils import timezone

# status=models.TextChoices("status", "Approved Not_Approved Pending")
# status1=models.TextChoices("status", "Returned Not_Returned")


# def overdue():
#     return date.today() + timedelta(days=14)


# class Registration(models.Model):
#     Roll_no=models.CharField(max_length=25, primary_key=True)
#     User_name=models.CharField(max_length=50)
#     Password=models.CharField(max_length=50)
#     Name=models.CharField(max_length=50)
#     Phn_no=models.IntegerField(unique=True)
#     Batch=models.CharField(max_length=20)

#     def __str__(self):
#         return self.Name
    
# class Book_details(models.Model):
#     Book_name=models.CharField(max_length=100)
#     Authors_name=models.CharField(max_length=100)
#     ISBN=models.CharField(primary_key=True)
#     Genre=models.CharField(max_length=50)
#     Language=models.CharField(max_length=50)
#     No_of_copies=models.IntegerField(validators=[MinValueValidator(1)])
#     Available_books=models.IntegerField(validators=[MinValueValidator(0)])
#     Posessed=models.IntegerField(validators=[MinValueValidator(0)])
#     cover = models.ImageField(upload_to='covers/', null=True, blank=True)


#     def __str__(self):
#         return f"{self.Book_name} ({self.ISBN})"
    
# class Reservation(models.Model):
#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('APPROVED', 'Approved'),
#         ('NOT_APPROVED', 'Not Approved'),
#     ]
#     student = models.ForeignKey(Registration, on_delete=models.CASCADE)
#     book = models.ForeignKey(Book_details, on_delete=models.CASCADE)
#     reserved_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    
#     def __str__(self):
#         return f"{self.student.Roll_no} - {self.book.Book_name}"


# class Book_specefic(models.Model):
#     Access_no=models.IntegerField(primary_key=True)
#     ISBN=models.ForeignKey(Book_details, on_delete=models.CASCADE, related_name="Bk_specific_access")

#     def __str__(self):
#         return str(self.Access_no)



# class Transaction_table(models.Model):
#     Access_no=models.ForeignKey(Book_specefic, on_delete=models.PROTECT, related_name="transaction_access")
#     Owned_by=models.ForeignKey(Registration, on_delete=models.PROTECT, related_name="person")
#     Due_date=models.DateField(default=overdue)
#     Status=models.CharField(max_length=20, choices=status1.choices, default="Not_Returned")


# class Fine_table(models.Model):
#     Access_no=models.ForeignKey(Book_specefic, on_delete=models.PROTECT, related_name="fine_access")
#     Owned_by=models.ForeignKey(Registration, on_delete=models.PROTECT, related_name="individual")
#     Amount=models.IntegerField(validators=[MinValueValidator(1)])
#     Due_date=models.DateField(default=overdue)



from django.db import models
from django.core.validators import MinValueValidator
from datetime import date, timedelta


from django.db import models
from datetime import date

status = models.TextChoices("status", "Approved Not_Approved Pending")
status1 = models.TextChoices("status", "Returned Not_Returned")


def overdue():
    return date.today() + timedelta(days=14)


class Registration(models.Model):
    Roll_no = models.CharField(max_length=25, primary_key=True)
    User_name = models.CharField(max_length=50)
    Password = models.CharField(max_length=50)
    Name = models.CharField(max_length=50)
    Phn_no = models.IntegerField(unique=True)
    Batch = models.CharField(max_length=20)

    def __str__(self):
        return self.Name


class Book_details(models.Model):
    id = models.AutoField(primary_key=True)  # NEW: Auto increment ID
    ISBN = models.CharField(max_length=50, unique=True)  # ISBN still unique

    Book_name = models.CharField(max_length=100)
    Authors_name = models.CharField(max_length=100)
    Genre = models.CharField(max_length=50)
    Language = models.CharField(max_length=50)
    No_of_copies = models.IntegerField(validators=[MinValueValidator(1)])
    Available_books = models.IntegerField(validators=[MinValueValidator(0)])
    Posessed = models.IntegerField(validators=[MinValueValidator(0)])
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.Book_name} ({self.ISBN})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('NOT_APPROVED', 'Not Approved'),
    ]

    student = models.ForeignKey(Registration, on_delete=models.CASCADE)

    # Now FK uses ISBN instead of ID
    book = models.ForeignKey(
        Book_details,
        to_field='ISBN',
        db_column='ISBN',
        on_delete=models.CASCADE
    )

    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.student.Roll_no} - {self.book.Book_name}"


class Book_specefic(models.Model):
    Access_no = models.IntegerField(primary_key=True)

    # Uses ISBN as FK linking to Book_details.ISBN
    ISBN = models.ForeignKey(
        Book_details,
        to_field='ISBN',
        db_column='ISBN',
        on_delete=models.CASCADE,
        related_name="Bk_specific_access"
    )

    def __str__(self):
        return str(self.Access_no)


class Transaction_table(models.Model):
    Access_no = models.ForeignKey(
        Book_specefic,
        on_delete=models.PROTECT,
        related_name="transaction_access"
    )

    Owned_by = models.ForeignKey(
        Registration,
        on_delete=models.PROTECT,
        related_name="person"
    )

    Due_date = models.DateField(default=overdue)
    Status = models.CharField(max_length=20, choices=status1.choices, default="Not_Returned")


class Fine_table(models.Model):
    Access_no = models.ForeignKey(
        Book_specefic,
        on_delete=models.PROTECT,
        related_name="fine_access"
    )

    Owned_by = models.ForeignKey(
        Registration,
        on_delete=models.PROTECT,
        related_name="individual"
    )

    Amount = models.IntegerField(validators=[MinValueValidator(1)])
    Due_date = models.DateField(default=overdue)



# chatgpt:

class BookIssue(models.Model):
    book_name = models.CharField(max_length=100)
    issue_date = models.DateField()
    due_date = models.DateField()

    def calculate_fine(self):
        current_date = date.today()
        if current_date > self.due_date:
            fine = (current_date - self.due_date).days * 1
        else:
            fine = 0
        return fine
