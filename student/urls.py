from django.urls import path
from .import views 

urlpatterns = [
    path('sthome', views.sthome, name='sthome'),
    path('register', views.registration, name='register'), 
    path('student/login', views.login, name='student_login'),
    path('book_list', views.book_list, name='book_list'),
    path("reserve/<str:ISBN>", views.reserve_book_manual, name="reserve_book_manual"),
    path("myreservations", views.my_reservations, name="myreservations"),
    
    # action
    path('loginaction', views.student_login, name='loginaction'),
    path('registered', views.register, name='registered'),
    path('resevation_success',views.reservation_success, name="reservation_success"),
    path('registration_success',views.registration_success, name="registration_success"),

]

