from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Transaction_table,Book_copy,Reservation


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
