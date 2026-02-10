from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from common.models import Book_details, Reservation, Registration
from common.forms import Registrationform, Book_detailsform
from datetime import date, timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

def registration(request):
    forms= Registrationform()
    return render(request, 'registration.html',{'forms':forms})
def register(request):
    msg = ""
    if request.method == "POST":
        forms= Registrationform(request.POST)
        if forms.is_valid():
            user=forms.save()
            
            request.session['Roll_no']=user.Roll_no

            return redirect("registration_success")

        else:
            forms= Registrationform()
            return render(request, 'registration.html',{'forms':forms, "msg":msg})
            
            
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






def reserve_book_manual(request, ISBN):
    if 'Roll_no' not in request.session:
        return redirect("student_login")

    Roll_no = request.session.get('Roll_no')
    student = Registration.objects.get(Roll_no=Roll_no)
    book = Book_details.objects.get(ISBN=ISBN)

    # Check active reservations
    active_res_count = Reservation.objects.filter(
        student=student,
        status__in=["Pending", "Approved"]
    ).count()

    if active_res_count >= 2:
        return render(request, "manual_reservation.html", {
            "form": Reservationform(),
            "book": book,
            "student": student,
            "limit_reached": True,   # <-- Important
        })

    if request.method == "POST":
        form = Reservationform(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.student = student
            reservation.book = book
            reservation.save()
            return render(request, "reservation_success.html", {
                "student": student,
                "book": book
            })

    else:
        form = Reservationform()

    return render(request, "manual_reservation.html", {
        "form": form,
        "book": book,
        "student": student
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
    
   
    
