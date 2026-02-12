from django.urls import path
from .import views 

urlpatterns = [
    #login urls
    path("librarian/login",views.lib_login,name="lib_login"),
    path('librarian/home',views.lib_home,name="lib_home"),
    path('librarian/logout',views.lib_logout,name="lib_logout"),
   
    #books related urls
    path('librarian/add_book',views.add_book,name="add_book"),
    path("booklist",views.list_books,name='listofbooks'),
    path('edit-book/<str:ISBN>/', views.edit_book_page, name='edit_book_page'),
    path('update-book/<str:ISBN>/', views.update_book, name='update_book'),
    
    path("show_transaction", views.show_transaction, name="show_transaction"),
    
    path("book/map/<str:ISBN>/", views.bookmap, name="book_map"),
    path("book/map/<str:ISBN>/save/", views.isbnmap_action, name="isbnmap_action"),
    path('approve/<int:id>/', views.approve_reservation, name='approve_reservation'),
    path('reject/<int:id>/', views.reject_reservation, name='reject_reservation'),
    path('addcount/<str:ISBN>/', views.addcount, name='addcount'),
    path('reduct/<str:ISBN>/', views.reducecount, name='reduct'),
    path('reduceposessed/<str:ISBN>/', views.reduceposessed, name='reduceposessed'),
    path('delete/<str:ISBN>/', views.delete, name='delete'),
    # path('isbnmap', views.isbnmap, name='isbnmap'),

    #circulation service 
    path("circulation_service/", views.circulation_service, name="circulation_service"),
    path("librarian/collect/<int:txn_id>/",views.mark_collected,name="mark_collected"),
    path("librarian/collect/<int:txn_id>/", views.mark_collected, name="mark_collected"),
    path("librarian/return/<int:txn_id>/", views.mark_returned, name="mark_returned"),


    
]
