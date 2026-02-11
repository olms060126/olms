from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('paypage',views.paypage,name='paypage'),
    path('payaction/',views.payment_send,name='pay_action'),
    path('payreturn',views.payment_confo,name='payment_confo')
    


]

