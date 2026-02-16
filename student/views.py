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
from deepface import DeepFace
import numpy as np
import base64
import pickle
import cv2
from scipy.spatial.distance import cosine


def student_login(request):

    form = LoginForm()

    if request.method == "POST":

        email = request.POST.get('email')
        Password = request.POST.get('Password')

        try:
            user = Registration.objects.get(email=email, Password=Password)

            request.session['Roll_no'] = user.Roll_no
            request.session['email'] = user.email

            return redirect("sthome")

        except Registration.DoesNotExist:
            messages.error(request, "Invalid username or password")

    return render(request, "student/login.html", {'forms': form})


def face_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        image_data = request.POST.get("image")

        try:
            user = Registration.objects.get(email=email)

            if not user.face_encoding:
                return JsonResponse({
                    "status": "no_face",
                    "message": "No face registered. Please use password."
                })

            format, imgstr = image_data.split(';base64,')
            image_bytes = base64.b64decode(imgstr)

            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            embedding_obj = DeepFace.represent(
                frame,
                model_name="ArcFace",
                enforce_detection=True
            )

            new_embedding = embedding_obj[0]["embedding"]
            stored_embedding = pickle.loads(user.face_encoding)

            from scipy.spatial.distance import cosine
            distance = cosine(stored_embedding, new_embedding)

            if distance < 0.5:

                request.session['Roll_no'] = user.Roll_no
                request.session['User_name'] = user.Name

                return JsonResponse({
                    "status": "success",
                    "redirect_url": "/sthome/"
                })

            else:
                return JsonResponse({
                    "status": "fail",
                    "message": "Face not recognized"
                })

        except Registration.DoesNotExist:
            return JsonResponse({
                "status": "fail",
                "message": "User not found"
            })



#Save the user registration first then redirecting to face registration

def register(request):
    if request.method == "POST":
        form = Registrationform(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.Password = form.cleaned_data['Password']

            user.save()

            messages.success(request, "Account created. Please register your face.")
            return redirect("face_register", roll_no=user.Roll_no)

        else:
            messages.error(request, "Registration failed")

    else:
        form = Registrationform()

    return render(request, "student/registration.html", {"forms": form})

def face_register_page(request, roll_no):
    user = get_object_or_404(Registration, Roll_no=roll_no)
    return render(request, "student/face_register.html", {"user": user})


#Ajax end point to save face encoding
def save_face_encoding(request, roll_no):

    if request.method == "POST":
        user = get_object_or_404(Registration, Roll_no=roll_no)

        image_data = request.POST.get("image")

        try:
            format, imgstr = image_data.split(';base64,')
            image_bytes = base64.b64decode(imgstr)

            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            embedding_obj = DeepFace.represent(
                frame,
                model_name="ArcFace",
                enforce_detection=True
            )

            embedding = embedding_obj[0]["embedding"]

            # store as binary
            user.face_encoding = pickle.dumps(embedding)
            user.save()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})



#js call to cancel reservation
def cancel_reservation(request, res_id):

    reservation = get_object_or_404(Reservation, id=res_id)

    if reservation.status in ["COLLECTED", "EXPIRED"]:
        return JsonResponse({
            "success": False,
            "message": "Cannot cancel this reservation"
        })

    reservation.status = "CANCELLED"
    reservation.save()

    return JsonResponse({"success": True})   



def sthome(request):

    

    student_logged = request.session.get('email') 
    student = get_object_or_404(Registration,email=student_logged)
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

    query = request.GET.get("q","")
    if query:
        books = books.filter(
            Q(Book_name__icontains=query)|
            Q(Authors_name__icontains=query)|
            Q(Genre__icontains=query)

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
        .prefetch_related("finetable")
        .order_by("-issued_on")
    )

    

    # ACTIVITY SUMMARY
    

    total_reserved = Reservation.objects.filter(
        student=student
    ).count()

    total_issued = student_transactions.filter(
        returned=False
    ).count()

    student_fines = Fine_table.objects.filter(
        transaction__Owned_by=student
    )

    total_fine_paid = student_fines.filter(
        paid=True
    ).aggregate(total=Sum("amount_payable"))["total"] or 0

    pending_fines = student_fines.filter(
        paid=False
    ).aggregate(total=Sum("amount_payable"))["total"] or 0
    

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
    
   
    
