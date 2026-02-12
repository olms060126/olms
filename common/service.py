
from datetime import timedelta
from django.db import transaction
from .models import Transaction_table,Book_copy,Reservation,Fine_table
from .util import send_mail
from django.utils import timezone
from datetime import date

FINE_PER_DAY = 10

def allocate_books():

    with transaction.atomic():

        available_copies = Book_copy.objects.filter(is_available=True)

        for copy in available_copies:

            reservations = (
                Reservation.objects
                .filter(
                    book__book=copy.book,
                    status='PENDING'
                )
                .order_by('reserved_at')
            )

            for res in reservations:

                active_books = Transaction_table.objects.filter(
                    Owned_by=res.student,
                    returned=False
                ).count()

                if active_books >= 4:
                    continue  # Skip student

                # Allocate
                res.book = copy
                res.status = 'ALLOCATED'
                res.allocated_at = timezone.now()
                res.save()
                #send notifiation to students about allocation
                student_email = res.student.email
                book_title = res.book.book.Book_name
                send_mail(
                    subject="Book Allocation Notification",
                    body=f"""Dear {res.student.Name},\n\nThe book '{book_title}' has been allocated to you
                    . Please collect it within 3 days.\n\nThank you. Or your book reservation will be expired after 3 days.""",
                    reseiver=student_email,
                )


                Transaction_table.objects.create(
                    Access_no=copy,
                    Owned_by=res.student
                )

                copy.is_available = False
                copy.save()

                break  # Move to next copy


def expire_uncollected():

    expiry_time = timezone.now() - timedelta(days=3)

    expired_reservations = Reservation.objects.filter(
        status='ALLOCATED',
        allocated_at__lt=expiry_time
    )

    for res in expired_reservations:
        res.status = 'EXPIRED'
        res.book.is_available = True
        res.book.save()
        res.save()



def calculate_fines():

    today = date.today()

    overdue_transactions = Transaction_table.objects.filter(
        collected=True,
        returned=False,
        Due_date__lt=today
    )

    for txn in overdue_transactions:

        overdue_days = (today - txn.Due_date).days
        fine_amount = overdue_days * FINE_PER_DAY

        fine_obj, created = Fine_table.objects.get_or_create(
            transaction=txn,
            defaults={"amount_payable": fine_amount}
        )

        if not created:
            fine_obj.amount_payable = fine_amount
            fine_obj.save()


def send_due_reminders():

    reminder_date = date.today() + timedelta(days=3)

    transactions = Transaction_table.objects.filter(
        collected=True,
        returned=False,
        Due_date=reminder_date
    )

    for txn in transactions:

        send_mail(
            subject="Library Due Reminder",
            message=f"""
Dear {txn.Owned_by.Name},

Your book "{txn.Access_no.book.Book_name}"
is due on {txn.Due_date}.

Fine policy: ₹10 per overdue day.

Please return it on time.

Library Management
""",
            from_email="library@yourdomain.com",
            recipient_list=[txn.Owned_by.email],
            fail_silently=True,
        )