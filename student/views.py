from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from common.models import Book_details, Reservation, Registration,Book_details, Book_copy, Reservation
from common.forms import Registrationform, Book_detailsform
from datetime import date, timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def registration(request):
    forms= Registrationform()
    return render(request, 'student/registration.html',{'forms':forms})


def register(request):
    msg = ""
    if request.method == "POST":
        forms= Registrationform(request.POST)
        if forms.is_valid():
            user=forms.save()
            
            request.session['Roll_no']=user.Roll_no

            return redirect("sthome")

        else:
            forms= Registrationform()
            return render(request, 'student/registration.html',{'forms':forms, "msg":msg})
            
            
def sthome(request):
    return render(request, 'homestudent.html')

def blist(request):
    items=Book_details.objects.all()
    return render(request, 'list.html', {'items':items})



def book_list(request):
    books = Book_details.objects.all()
    return render(request, "book_list.html", {"books": books})



def student_login(request):
    if request.method == "POST":
        User_name= request.POST.get('User_name')
        Password= request.POST.get('Password')

        try:
            user= Registration.objects.get(User_name=User_name,Password=Password)
            request.session['Roll_no']=user.Roll_no
            request.session['User_name']=user.User_name
            return redirect("book_list")      

        except Registration.DoesNotExist:
                return HttpResponse("login unsuccesful")
    return render(request,"login.html")
        
        

    
def login(request):
    forms= Registrationform()
    return render(request, 'login.html',{'forms':forms})






@require_POST
def ajax_reserve_book(request, book_id):

    student = request.user.registration  # adjust if needed

    try:
        book = Book_details.objects.get(id=book_id)
    except Book_details.DoesNotExist:
        return JsonResponse({"success": False, "error": "Book not found"})

    
    if Reservation.objects.filter(
        student=student,
        book__book=book,
        status="PENDING"
    ).exists():
        return JsonResponse({"success": False, "error": "Already reserved"})

    
    copy = Book_copy.objects.filter(
        book=book,
        is_available=True
    ).first()

    if not copy:
        return JsonResponse({"success": False, "error": "No copies available"})

    with transaction.atomic():
        Reservation.objects.create(
            student=student,
            book=copy,
            status="PENDING"
        )

        copy.is_available = False
        copy.save()

    return JsonResponse({
        "success": True,
        "available_copies": book.copies.filter(is_available=True).count()
    })




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
    
   
    
