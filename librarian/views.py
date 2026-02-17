from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from common.models import (
    Registration,
      Book_details,
        Reservation,
        Book_copy,
          Transaction_table,
          Librarian,
          Fine_table,Books_online_copies)
from common.forms import Book_detailsform,LibrarianForm,BooksOnlineForm
from django.contrib import messages
from django.db.models import Q,Count
from django.db import transaction
from django.db.models import F
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from common.util import send_mail
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import date


from common.service import expire_uncollected,allocate_books,send_due_reminders,calculate_fines


#Login logics
def lib_login(request):
    form = LibrarianForm()
    if request.POST:
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        print(user_name,password)
        try:
            librarian = get_object_or_404(
                Librarian,
                user_name=user_name,
                password=password
            )
            return redirect('lib_home')
        except Exception as e:
            messages.error(request,f"Invalid credentials {str(e)}")
    return render(request,'librarian/liblogin.html',{'forms':form})
            

#home page of librarian
def lib_home(request):


    total_books = Book_details.objects.count()
    total_copies = Book_copy.objects.count()

    available_copies = Book_copy.objects.filter(
        is_available=True
    ).count()

    # Active issued books = collected but not returned
    issued_books = Transaction_table.objects.filter(
        collected=True,
        returned=False
    ).count()

    # Allocated but not yet collected
    pending_collection = Transaction_table.objects.filter(
        collected=False,
        returned=False
    ).count()

    total_students = Registration.objects.count()

    pending_reservations = Reservation.objects.filter(
        status="PENDING"
    ).count()

    allocated_reservations = Reservation.objects.filter(
        status="ALLOCATED"
    ).count()

  

    stats = [
        ("Books", total_books),
        ("Copies", total_copies),
        ("Available", available_copies),
        ("Issued", issued_books),
        ("Pending Collection", pending_collection),
        ("Students", total_students),
        ("Pending Reservations", pending_reservations),
        ("Allocated Reservations", allocated_reservations),
    ]

    context = {
        "stats": stats,
        "available_copies": available_copies,
        "issued_books": issued_books,
        "pending_collection": pending_collection,
        "total_books": total_books,
        "total_copies": total_copies,
        "total_students": total_students,
        "pending_reservations": pending_reservations,
        "allocated_reservations": allocated_reservations,
    }

    return render(request, "librarian/libhome.html", context)


FINE_PER_DAY = 10
@require_POST
def mark_returned(request, txn_id):
    print(f"Marking transaction {txn_id} as returned")
    txn = get_object_or_404(Transaction_table, id=txn_id)

    if txn.returned:
        return JsonResponse({
            "success": False,
            "message": "Already returned"
        })

    today = date.today()

    txn.returned = True
    txn.Access_no.is_available = True
    txn.Access_no.save()
    txn.save()

    fine_amount = 0

    if today > txn.Due_date:
        overdue_days = (today - txn.Due_date).days
        fine_amount = overdue_days * FINE_PER_DAY

        Fine_table.objects.update_or_create(
            transaction=txn,
            defaults={
                "amount_payable": fine_amount,
                "paid": False
            }
        )
    reservation = Reservation.objects.filter(
        student=txn.Owned_by,
        book=txn.Access_no,
        status="COLLECTED"
    ).first()

    if reservation:
        reservation.status = "COMPLETED"
        reservation.save()


    return JsonResponse({
        "success": True,
        "fine_amount": fine_amount,
        "transaction_id": txn.id
    })
#Allocation of books


#edit
def get_book_data(request, ISBN):

    book = get_object_or_404(Book_details, ISBN=ISBN)

    return JsonResponse({
        "id": book.id,
        "Book_name": book.Book_name,
        "Authors_name": book.Authors_name,
        "Genre": book.Genre,
        "Language": book.Language,
    })




@require_POST
def update_book(request, ISBN):

    book = get_object_or_404(Book_details, ISBN=ISBN)

    book.Book_name = request.POST.get("bookname")
    book.Authors_name = request.POST.get("auther")
    book.Genre = request.POST.get("genre")
    book.Language = request.POST.get("language")

    book.save()

    return JsonResponse({"success": True})
def pay_fine(request, txn_id):

    txn = get_object_or_404(Transaction_table, id=txn_id)
    fine = get_object_or_404(Fine_table, transaction=txn)

    fine.paid = True
    fine.save()

    return JsonResponse({"success": True})



@require_POST
def mark_collected(request, txn_id):
    
    try:
        txn = Transaction_table.objects.get(id=txn_id)
        student = txn.Owned_by
        print(student.email)

        if txn.returned:
            return JsonResponse({"success": False, "error": "Already returned"})

        txn.collected = True
        txn.save()
        reservation = Reservation.objects.filter(
        student=txn.Owned_by,
        book=txn.Access_no,
        status="ALLOCATED"
    ).first()
        if reservation:
            reservation.status = "COLLECTED"
            reservation.save()
        subject = "Book Collection Confirmation"
        message = f""" Dear {{student.Name}},\n\n
        you have successfully collected the book
        '{txn.Access_no.book.Book_name}' (ISBN: {txn.Access_no.book.ISBN}) on {txn.issued_on.strftime('%Y-%m-%d %H:%M:%S')}.
        Please return the book within 14 days to avoid late fees.\n\n"""
        send_mail(
            reseiver=student.email, 
            subject = subject ,
            body= message)

        return JsonResponse({"success": True})

    except Transaction_table.DoesNotExist:
        return JsonResponse({"success": False}, status=404)

def library_auto_service(request):
    send_due_reminders()
    calculate_fines()
    return JsonResponse({"status":"ok"})



#buisiness logic for circulation service
def circulation_service(request):
    expire_uncollected()
    allocate_books()
    return JsonResponse({"status": "ok"})



#add books
def lib_logout(request):
    request.session.flush()
    return redirect('home')


def add_book(request):
    if request.method == "POST":
        form = Book_detailsform(request.POST, request.FILES)
        try:
            if form.is_valid():
                copies = form.cleaned_data.pop("number_of_copies")

                with transaction.atomic():
                    book = form.save()

                    Book_copy.objects.bulk_create([
                    Book_copy(book=book)
                    for _ in range(copies)
                 ])
            messages.info(request,f"{request.POST.get('Book_name')} added to collection")
            return redirect("add_book")
        except Exception as e:
            messages.error(request,"failed to add {e}")
    form = Book_detailsform()
    return render(request, "librarian/bookinfo.html", {"forms": form})



def list_books(request):
    query = request.GET.get("q", "").strip()

    books = (
        Book_details.objects
        .annotate(
            total_copies=Count("copies"),
            available_copies=Count(
                "copies",
                filter=Q(copies__is_available=True)
            )
        )
    )

    if query:
        books = books.filter(
            Q(ISBN__icontains=query) |
            Q(Book_name__icontains=query)
        )

    context = {
        "books": books,
        "query": query,
        "total_books": Book_details.objects.count(),
    }

    return render(request, "librarian/bolist.html", context)


def online_books(request):

    search_query = request.GET.get("search", "")
    genre_filter = request.GET.get("genre", "")
    edit_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")

    # Delete
    if delete_id:
        Books_online_copies.objects.filter(id=delete_id).delete()
        return redirect("online_books")

    # Edit
    if edit_id:
        book_instance = get_object_or_404(Books_online_copies, id=edit_id)
    else:
        book_instance = None

    if request.method == "POST":
        form = BooksOnlineForm(request.POST, request.FILES, instance=book_instance)
        if form.is_valid():
            form.save()
            return redirect("online_books")
    else:
        form = BooksOnlineForm(instance=book_instance)

    books = Books_online_copies.objects.all()

    # Search
    if search_query:
        books = books.filter(title__icontains=search_query)

    # Genre Filter
    if genre_filter:
        books = books.filter(genre=genre_filter)

    # Stats
    total_books = books.count()
    genre_stats = Books_online_copies.objects.values("genre").annotate(count=Count("id"))

    # Pagination
    paginator = Paginator(books, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "books": page_obj,
        "total_books": total_books,
        "genre_stats": genre_stats,
        "search_query": search_query,
        "genre_filter": genre_filter,
        "edit_book": book_instance,
    }

    return render(request, "librarian/online_books.html", context)


def owned_by(request, ISBN):
    book = get_object_or_404(Book_details, ISBN=ISBN)

    transactions = Transaction_table.objects.filter(
        Access_no__book=book,
        collected=True,
        returned=False
    ).select_related("Owned_by")

    context = {
        "book": book,
        "transactions": transactions
    }

    return render(request, "librarian/owned_by.html", context)


def approve_reservation(request, id):
    reservation= get_object_or_404(Reservation, id=id)
    
    if reservation.status=="Pending":
        reservation.status= "Approved"
        reservation.save()
        book= Book_details.objects.get(ISBN=reservation.book.ISBN)
        if book.Available_books != 0:
            Book_details.objects.filter(ISBN=reservation.book.ISBN).update(
                Available_books= F('Available_books') - 1,
                Posessed= F('Posessed') + 1
            ) 
    return redirect("reservationdetails")


def notapprove_reservation(request, id):
    reservation= get_object_or_404(Reservation, id=id)
    
    if reservation.status=="Pending":
        reservation.status= "Not Approved"
        reservation.save()
        book= Book_details.objects.get(ISBN=reservation.book.ISBN)
        if book.Available_books != 0:
            Book_details.objects.filter(ISBN=reservation.book.ISBN).update(
                Available_books= F('Available_books') - 1,
                Posessed= F('Posessed') + 1
            ) 
    return redirect("reservationdetails")





def reject_reservation(request, id):
    reservation= get_object_or_404(Reservation, id=id)
    reservation.status= "Not Approved"
    reservation.save()
    return redirect("reservation_details")

def reducecount(request, ISBN):
    count=get_object_or_404(Book_details, ISBN=ISBN)
    if count.No_of_copies > 1:
            Book_details.objects.filter(ISBN=ISBN).update(
                No_of_copies= F('No_of_copies') - 1,
                Available_books= F('Available_books') - 1
            ) 
    return redirect("bolist")

def addcount(request, ISBN):
    count=get_object_or_404(Book_details, ISBN=ISBN)
    Book_details.objects.filter(ISBN=ISBN).update(
        No_of_copies= F('No_of_copies') + 1,
        Available_books= F('Available_books') + 1
        ) 
    return redirect("bolist")

def reduceposessed(request, ISBN):
    count=get_object_or_404(Book_details, ISBN=ISBN)
    if count.Posessed >= 1:
        Book_details.objects.filter(ISBN=ISBN).update(
            Posessed= F('Posessed') - 1,
        ) 
    return redirect("bolist")

def delete(request, ISBN):
    book=get_object_or_404(Book_details, ISBN=ISBN)
    if request.method=='POST':
        print("deleting book")
        book.delete()
    return JsonResponse({"success": True})







def add_book_action(request):
    if request.method != "POST":
        return redirect("add_book_page")  # redirect if GET

    # include request.FILES to handle uploaded files
    form = Book_detailsform(request.POST, request.FILES)

    if form.is_valid():
        # Save Book_details including cover
        book = Book_details.objects.create(
            Book_name=form.cleaned_data["Book_name"],
            Authors_name=form.cleaned_data["Authors_name"],
            ISBN=form.cleaned_data["ISBN"],
            Genre=form.cleaned_data["Genre"],
            Language=form.cleaned_data["Language"],
            No_of_copies=form.cleaned_data["No_of_copies"],
            Available_books=form.cleaned_data["Available_books"],
            Posessed=form.cleaned_data["Posessed"],
            cover=form.cleaned_data.get("cover"),  # add this line
            description =form.cleaned_data.get('description')

        )
        # Save Book_specefic
        Book_copy.objects.create(
            Access_no=form.cleaned_data["Access_no"],
            ISBN=book,
        )
        return redirect("bolist")  # success page
    # If form invalid → re-render page with errors
    return render(request, "add_book_and_copy.html", {"form": form})


def bookmap(request, ISBN):
    book = Book_details.objects.get(ISBN=ISBN)
    form = Book_copy()
    return render(request, 'isbnmap.html', {'form': form, 'book': book})

def isbnmap_action(request, ISBN):
    book = Book_details.objects.get(ISBN=ISBN)

    if request.method == "POST":
        form = Book_copy(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            # Assign the foreign key properly
            obj.ISBN = book      # <-- THIS IS THE CORRECT WAY

            obj.save()
            return HttpResponse("Access number added successfully!")
    
    return HttpResponse("Invalid Request")





def show_transaction(request):

    transactions = (
        Transaction_table.objects
        .select_related("Owned_by", "Access_no__book")
        .all()
        .order_by("-issued_on")
    )

 
    query = request.GET.get("q", "").strip()
    if query:
        transactions = transactions.filter(
            Q(Owned_by__User_name__icontains=query) |
            Q(Access_no__book__Book_name__icontains=query) |
            Q(Access_no__book__ISBN__icontains=query)
        )

  
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        transactions = transactions.filter(
            issued_on__date__gte=parse_date(start_date)
        )

    if end_date:
        transactions = transactions.filter(
            issued_on__date__lte=parse_date(end_date)
        )

    paginator = Paginator(transactions, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "transactions": page_obj,
        "page_obj": page_obj,
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "librarian/show_transactions.html", context)



#fine dashbord
def fine_dashboard(request):

    fines = Fine_table.objects.select_related(
        "transaction__Owned_by",
        "transaction__Access_no__book"
    )

 
    total_fines = fines.aggregate(
        total=Sum("amount_payable")
    )["total"] or 0

    total_paid = fines.filter(
        paid=True
    ).aggregate(total=Sum("amount_payable"))["total"] or 0

    total_unpaid = fines.filter(
        paid=False
    ).aggregate(total=Sum("amount_payable"))["total"] or 0

  
    monthly_data = (
        fines
        .annotate(month=TruncMonth("transaction__issued_on"))
        .values("month")
        .annotate(total=Sum("amount_payable"))
        .order_by("month")
    )

    months = [m["month"].strftime("%b %Y") for m in monthly_data if m["month"]]
    monthly_totals = [m["total"] for m in monthly_data]

    top_defaulters = (
        fines.filter(paid=False)
        .values("transaction__Owned_by__Name")
        .annotate(total=Sum("amount_payable"))
        .order_by("-total")[:5]
    )

    defaulter_names = [
        d["transaction__Owned_by__Name"]
        for d in top_defaulters
    ]

    defaulter_amounts = [
        d["total"]
        for d in top_defaulters
    ]

    context = {
        "total_fines": total_fines,
        "total_paid": total_paid,
        "total_unpaid": total_unpaid,
        "months": months,
        "monthly_totals": monthly_totals,
        "defaulter_names": defaulter_names,
        "defaulter_amounts": defaulter_amounts,
    }

    return render(request, "librarian/fine_dashboard.html", context)


def librarian_login(request):
    if request.method == "POST":
        User_name= request.POST.get('User_name')
        Password= request.POST.get('Password')

        try:
            user= Registration.objects.get(User_name=User_name,Password=Password)
            
            request.session['User_name']=user.User_name
            return redirect("libhome")      

        except Registration.DoesNotExist:
                return HttpResponse("login unsuccesful")
    return render(request,"liblogin.html")