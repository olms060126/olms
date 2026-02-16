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
    path('student/cancel_reservation/<int:res_id>',views.cancel_reservation, name="cancel_reservartion"),

    path("face-register/<str:roll_no>/", views.face_register_page, name="face_register"),
    path("save-face/<str:roll_no>/", views.save_face_encoding, name="save_face"),

    path("face-login/", views.face_login, name="face_login"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path("student-online-books/", views.online_books_students, name="online_books_students"),



]

