from django.urls import path
from .import views 

urlpatterns = [
    path('bookinfo', views.bookinfo, name='bookinfo'),
    path('transaction', views.transaction_details, name='transaction'),
    path('fine', views.fine_details, name='fine'),
    path('libhome', views.libhome, name='libhome'),
    path('bolist', views.bolist, name='bolist'),
    path('reservationdetails', views.reservationdetails, name='reservationdetails'),
    # path('map', views.bookmap, name='map'),
    path('edit-book/<str:ISBN>/', views.edit_book_page, name='edit_book_page'),
    path('update-book/<str:ISBN>/', views.update_book, name='update_book'),
    path("add-book/", views.add_book_page, name="add_book_page"),
    path("add-book/save/", views.add_book_action, name="add_book_action"),
    
    path("show_transaction", views.show_transaction, name="show_transaction"),
    path("liblogin", views.liblogin, name="liblogin"),
    path("libregistration", views.libregistration, name="libregistration"),
    path("issued_books", views.issued_books, name="issued_books"),
    path("libregistrationsuccess", views.libregistration_success, name="libregistrationsuccess"),
    
    path("book/map/<str:ISBN>/", views.bookmap, name="book_map"),
    path("book/map/<str:ISBN>/save/", views.isbnmap_action, name="isbnmap_action"),



    path('libloginaction', views.librarian_login, name='libloginaction'),

    path('trans', views.trans, name='trans'),
    path('approve/<int:id>/', views.approve_reservation, name='approve_reservation'),
    path('reject/<int:id>/', views.reject_reservation, name='reject_reservation'),
    path('addcount/<str:ISBN>/', views.addcount, name='addcount'),
    path('reduct/<str:ISBN>/', views.reducecount, name='reduct'),
    path('reduceposessed/<str:ISBN>/', views.reduceposessed, name='reduceposessed'),
    path('delete/<str:ISBN>/', views.delete, name='delete'),
    # path('isbnmap', views.isbnmap, name='isbnmap'),
    
]
