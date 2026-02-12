


from django.db import models
from django.core.validators import MinValueValidator
from datetime import date, timedelta
from django.utils import timezone


from django.db import models
from datetime import date

status = models.TextChoices("status", "Approved Not_Approved Pending")
status1 = models.TextChoices("status", "Returned Not_Returned")


def overdue():
    return date.today() + timedelta(days=14)

# Registration model + login details
class Registration(models.Model):
    Roll_no = models.CharField(max_length=25, primary_key=True)
    User_name = models.CharField(max_length=50,unique=True)
    Password = models.CharField(max_length=50)
    Name = models.CharField(max_length=50)
    Phn_no = models.IntegerField(unique=True)
    Batch = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.Name

#book detail model  (individual book details)
class Book_details(models.Model):
    Genre_Choice = [
        ('HORROR', 'horror'),
        ('NOVEL', 'novel'),
        ('POEMS', 'poems'),
        ('EXAM ORIENTED','examoriented')
    ]
    Language_Choice=[
        ('ENGLISH','ENGLISH'),
        ('MALAYALAM','MALAYALAM'),
        ('HINDI','HINDI')
    ]
    ISBN = models.CharField(max_length=50, unique=True,)  # ISBN still unique
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    Book_name = models.CharField(max_length=100)
    Authors_name = models.CharField(max_length=100)
    Genre = models.CharField(max_length=50,choices=Genre_Choice)
    Language = models.CharField(max_length=50,choices=Language_Choice)
    description = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.Book_name} ({self.ISBN})"
    

#Number of physical copies of the book
class Book_copy(models.Model):
    STATUS_CHOICES = [
        ('HORROR', 'horror'),
        ('NOVEL', 'novel'),
        ('POEMS', 'poems'),
        ('EXAM ORIENTED','examoriented')
    ]
    book= models.ForeignKey(
        Book_details,
        on_delete = models.CASCADE,
        related_name='copies'
    )
    is_available= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.Book_name}"
    
    


#Book reveservation model
class Reservation(models.Model):

    STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('ALLOCATED', 'Allocated'),
    ('COLLECTED', 'Collected'),
    ('COMPLETED', 'Completed'),
    ('EXPIRED', 'Expired'),
    ('CANCELLED', 'Cancelled'),
]



    student = models.ForeignKey(Registration, on_delete=models.CASCADE)

    book = models.ForeignKey(
        Book_copy,
        related_name='reservations',
        on_delete=models.CASCADE
    )

    reserved_at = models.DateTimeField(auto_now_add=True)

    allocated_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    class Meta:
        ordering = ['reserved_at']

    #making sure a student can only have one active reservation per book
    def save(self, *args, **kwargs):
        if self.status == 'PENDING':
            existing = Reservation.objects.filter(
                student=self.student,
                book__book=self.book.book,
                status='PENDING'
            ).exclude(id=self.id)

            if existing.exists():
                raise ValueError("You already have a pending reservation for this book.")

        super().save(*args, **kwargs)


class Transaction_table(models.Model):

    Access_no = models.ForeignKey(
        Book_copy,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    Owned_by = models.ForeignKey(
        Registration,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    issued_on = models.DateTimeField(auto_now_add=True)
    collected = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)

    Due_date = models.DateField(default=overdue)

    def __str__(self):
        return f"{self.Access_no} - {self.Owned_by}"
    
    # making sure a student cant keep multiple copies of the same book
    def save(self, *args, **kwargs):
        if not self.pk:  # Only check on creation
            existing = Transaction_table.objects.filter(
                Owned_by=self.Owned_by,
                Access_no__book=self.Access_no.book,
                returned=False

            )

            if existing.exists():
                raise ValueError("You already have an active transaction for this book.")

        super().save(*args, **kwargs)


class Fine_table(models.Model):
    transaction = models.OneToOneField(

        Transaction_table,
        on_delete=models.CASCADE,
        related_name="finetable"
    )
    amount_payable = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)







#Librarial model
class Librarian(models.Model):
    user_name =models.CharField(max_length=50,unique=True)
    password  = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True,)

    def __str__(self):
        return self.name



