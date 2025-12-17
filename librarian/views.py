from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from common.models import Registration, Book_details, Reservation,Book_specefic, Transaction_table, BookIssue
from common.forms import Book_detailsform, Transactionform, Fineform, Book_speceficform, BookEditForm, BookCombinedForm, Registrationform


from django.db.models import F

def bookinfo(request):
    msg = ""
    if request.method == "POST":
        forms= Book_detailsform(request.POST)
        if forms.is_valid():
            forms.save()

            return HttpResponse("entered succesfully")
        else:
            return HttpResponse("unsuccessful")
    else:
        forms= Book_detailsform()
        return render(request, 'bookinfo.html',{'forms':forms, "msg":msg})


def transaction_details(request):
    ret= Transactionform
    return render(request, 'transaction.html',{'forms':ret})
def trans(request):
    if request.POST:
        ret=Transactionform(request.POST)
        if ret.is_valid():
            ret.save()
            return HttpResponse("transaction complete")
        else:
            return HttpResponse("transaction incomplete")

def fine_details(request):
    res= Fineform
    return render(request, 'fine.html',{'forms':res})

def libhome(request):
    return render(request, 'libhome.html')

def bolist(request):
    books=Book_details.objects.all()
    return render(request, 'bolist.html', {'books':books})

def reservationdetails(request):
    reservations = Reservation.objects.all()
    return render(request, "reservationdetails.html", {"reservations": reservations})

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

def liblogin(request):
    forms= Registrationform()
    return render(request, 'liblogin.html',{'forms':forms})

def libregistration(request):
    forms= Registrationform()
    return render(request, 'libregistration.html',{'forms':forms})



# def approve_reservation(request, id):
#     reservation = get_object_or_404(Reservation, id=id)

#     active_count = Reservation.objects.filter(
#         student=reservation.student,
#         status__in=["Pending", "Approved"]  
#     ).count()

#     if active_count >= 2:

#         from django.contrib import messages
#         messages.error(request, "This student already has 2 active reservations.")
#         return redirect("reservation_details")


#     if reservation.status == "Pending":
#         reservation.status = "Approved"
#         reservation.save()

#         book = Book_details.objects.get(ISBN=reservation.book.ISBN)

#         if book.Available_books > 0:
#             Book_details.objects.filter(ISBN=reservation.book.ISBN).update(
#                 Available_books=F('Available_books') - 1,
#                 Posessed=F('Posessed') + 1
#             )

#     return redirect("reservation_details")


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

# def bookmap(request):
#     mapped= Book_speceficform()
#     return render(request, 'isbnmap.html',{'mapped':mapped})

# def isbnmap(request):
#     if request.method == "POST":
#         mapped= Book_speceficform(request.POST)
#         if mapped.is_valid():
#             mapped.save()

#             return HttpResponse("registration_success")

#     else:
#         return HttpResponse("registration_success")
    
# def my_reservations(request):
#     Roll_no=request.session.get("Roll_no")
#     resd= Reservation.objects.filter(student_id=Roll_no)
#     return render(request, "my_reservations.html", {"resd":resd})



def edit_book_page(request, ISBN):
    book = get_object_or_404(Book_details, ISBN=ISBN)
    form = BookEditForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})

def update_book(request, ISBN):
    book = get_object_or_404(Book_details, ISBN=ISBN)

    if request.method == "POST":
        form = BookEditForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('bolist')  

    
    form = BookEditForm(request.POST, instance=book)
    return render(request, 'librarian/edit_book.html', {'form': form, 'book': book})






def add_book_page(request):
    form = BookCombinedForm()
    return render(request, "add_book_and_copy.html", {"form": form})

def add_book_action(request):
    if request.method != "POST":
        return redirect("add_book_page")  # redirect if GET

    # include request.FILES to handle uploaded files
    form = BookCombinedForm(request.POST, request.FILES)

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
        Book_specefic.objects.create(
            Access_no=form.cleaned_data["Access_no"],
            ISBN=book,
        )
        return redirect("bolist")  # success page
    # If form invalid → re-render page with errors
    return render(request, "add_book_and_copy.html", {"form": form})


def bookmap(request, ISBN):
    book = Book_details.objects.get(ISBN=ISBN)
    form = Book_speceficform()
    return render(request, 'isbnmap.html', {'form': form, 'book': book})

def isbnmap_action(request, ISBN):
    book = Book_details.objects.get(ISBN=ISBN)

    if request.method == "POST":
        form = Book_speceficform(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            # Assign the foreign key properly
            obj.ISBN = book      # <-- THIS IS THE CORRECT WAY

            obj.save()
            return HttpResponse("Access number added successfully!")
    
    return HttpResponse("Invalid Request")

def show_transaction(request):
    transactions = (Transaction_table.objects.select_related('Owned_by','Access_no', 'Access_no__ISBN').all())
    return render(request, 'show_transactions.html',{'transactions': transactions})

def libregistration_success (request):
    form = Registrationform()
    return render(request, "libregistration_success.html", {"form": form})





def issued_books(request):
    books = BookIssue.objects.all()
    
    for book in books:
        book.fine = book.calculate_fine()

    return render(request, 'issued_books.html', {'books': books})




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