from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from common.models import Book_details, Reservation, Registration,Book_details, Book_copy, Reservation,Fine_table, Transaction_table
from common.forms import Registrationform, Book_detailsform,LoginForm
from datetime import date, timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Exists, OuterRef, Sum
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction


def student_login(request):
    forms = LoginForm()
    if request.method == "POST":

        User_name= request.POST.get('User_name')
        Password= request.POST.get('Password')
        

        try:
            user= Registration.objects.get(User_name=User_name,Password=Password)
            request.session['Roll_no']=user.Roll_no
            request.session['User_name']=user.User_name
            return redirect("sthome")      

        except Registration.DoesNotExist:
               messages.error(request,"invalid username or password")
    return render(request,"student/login.html",{'forms':forms})




def register(request):
    if request.method == "POST":
        form = Registrationform(request.POST)
        if form.is_valid():
            form.save()
            return redirect("student_login") 
        else:
            messages.error(request, "Registration failed")
    else:
        form = Registrationform()

    return render(request, "student/registration.html", {"forms": form})
         
            



def sthome(request):

    
    student_logged = request.session.get('User_name') 
    student = get_object_or_404(Registration,User_name=student_logged)
    books = (
        Book_details.objects
        .annotate(
            total_copies=Count("copies"),
            available_copies=Count(
                "copies",
                filter=Q(copies__is_available=True)
            ),
            is_reserved=Exists(
                Reservation.objects.filter(
                    student=student,
                    book__book=OuterRef("pk"),
                    status="PENDING"
                )
            )
        )
    )

    

   
    
    books_by_genre = {}

    for book in books:
        genre = book.Genre
        if genre not in books_by_genre:
            books_by_genre[genre] = []
        books_by_genre[genre].append(book)

    
    # STUDENT TRANSACTIONS
    

    student_transactions = (
        Transaction_table.objects
        .filter(Owned_by=student)
        .select_related("Access_no__book")
    )

    

    # ACTIVITY SUMMARY
    

    total_reserved = Reservation.objects.filter(
        student=student
    ).count()

    total_issued = student_transactions.count()

    fine_data = Fine_table.objects.all()
    total_fine_paid = fine_data.aggregate(
        total=Sum("amount_payable")
    )["total"] or 0

    # You can refine this if you add a "paid" field later
    pending_fines = total_fine_paid  

    context = {
        "student": student,
        "books_by_genre": books_by_genre,
        "student_transactions": student_transactions,
        "total_reserved": total_reserved,
        "total_issued": total_issued,
        "total_fine_paid": total_fine_paid,
        "pending_fines": pending_fines,
    }

    return render(request, "homestudent.html", context)


def stlogout(request):
    request.session.flush()
    return redirect('home')



def blist(request):
    items=Book_details.objects.all()
    return render(request, 'list.html', {'items':items})



def book_list(request):
    books = Book_details.objects.all()
    return render(request, "book_list.html", {"books": books})




        
    







@require_POST
def ajax_reserve_book(request, book_id):

    try:
        student_id = request.session.get("User_name")
        if not student_id:
            return JsonResponse({"success": False, "error": "Login required"}, status=400)

        student = Registration.objects.get(User_name=student_id)
        book = Book_details.objects.get(id=book_id)

        with transaction.atomic():

            # Check already reserved FIRST
            if Reservation.objects.filter(
                student=student,
                book__book=book,
                status="PENDING"
            ).exists():
                return JsonResponse({"success": False, "error": "Already reserved"}, status=200)

            copy = (
                Book_copy.objects
                .select_for_update()
                .filter(book=book, is_available=True)
                .first()
            )

            if not copy:
                return JsonResponse({"success": False, "error": "No copies available"}, status=200)

            Reservation.objects.create(
                student=student,
                book=copy,
                status="PENDING"
            )

            copy.is_available = False
            copy.save()

        return JsonResponse({"success": True}, status=200)

    except Exception as e:
        print("RESERVE ERROR:", e)  
        return JsonResponse({"success": False, "error": str(e)}, status=500)



def reservation_success(request):
    Roll_no=request.session.get("Roll_no")
    student=Registration.objects.get(Roll_no=Roll_no)
    
    book=Reservation.objects.filter(student=student).last().book
    
    return render(request, "reservation_success.html",{
        "student": student,
        "book": book
    })
def registration_success(request):
    Roll_no= request.session.get("Roll_no")
    student=Registration.objects.get(Roll_no=Roll_no)
    return render(request, "registration_success.html",{"student": student})
    
def my_reservations(request):
    Roll_no=request.session.get("Roll_no")
    resd= Reservation.objects.filter(student_id=Roll_no)
    return render(request, "my_reservations.html", {"resd":resd})
    
   
    
