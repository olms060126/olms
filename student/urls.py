from django.urls import path
from .import views 

urlpatterns = [
    path('sthome', views.sthome, name='sthome'),
    path('register', views.register, name='register'), 
    path('student/login', views.student_login, name='student_login'),
    path('student/logout',views.stlogout,name="stlogout"),
    path('book_list', views.book_list, name='book_list'),
    path("ajax/reserve/<int:book_id>", views.ajax_reserve_book, name="ajax_reserve_book"),
    path("myreservations", views.my_reservations, name="myreservations"),
    
    path('registered', views.register, name='registered'),
    path('resevation_success',views.reservation_success, name="reservation_success"),
    path('registration_success',views.registration_success, name="registration_success"),

]

