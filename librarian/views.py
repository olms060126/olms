from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from common.models import Registration, Book_details, Reservation,Book_copy, Transaction_table,Librarian
from common.forms import Book_detailsform,LibrarianForm
from django.contrib import messages
from django.db.models import Q,Count
from django.db import transaction
from django.db.models import F
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date

from common.service import expire_uncollected,allocate_books


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
    stats = [
        ("Books", Book_details.objects.count()),
        ("Copies", Book_copy.objects.count()),
        ("Available", Book_copy.objects.filter(is_available=True).count()),
        ("Issued", Transaction_table.objects.filter(status="NOT_RETURNED").count()),
        ("Students", Registration.objects.count()),
        ("Pending", Reservation.objects.filter(status="PENDING").count()),
    ]

    context = {
        "stats": stats,
        "available_copies": Book_copy.objects.filter(is_available=True).count(),
        "issued_books": Transaction_table.objects.filter(status="NOT_RETURNED").count(),
        "total_books": Book_details.objects.count(),
        "total_copies": Book_copy.objects.count(),
        "total_students": Registration.objects.count(),
        "pending_reservations": Reservation.objects.filter(status="PENDING").count(),
    }
    return render(request,'librarian/libhome.html',context)



#Allocation of books
def mark_collected(request, txn_id):

    txn = Transaction_table.objects.get(id=txn_id)
    txn.collected = True
    txn.save()

    return JsonResponse({"success": True})


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
        book.delete()
    return redirect("bolist")





def edit_book_page(request, ISBN):
    book = get_object_or_404(Book_details, ISBN=ISBN)
    form = Book_detailsform()
    return render(request, 'edit_book.html', {'form': form, 'book': book})

def update_book(request, ISBN):
    book = get_object_or_404(Book_details, ISBN=ISBN)

    if request.method == "POST":
        form = Book_detailsform(request.POST,)
        if form.is_valid():
            form.save()
            return redirect('bolist')  

    
    form = Book_detailsform(request.POST,)
    return render(request, 'librarian/edit_book.html', {'form': form, 'book': book})









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