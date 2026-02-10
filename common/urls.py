from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('paypage',views.paypage,name='paypage'),
    path('payaction/',views.payment_send,name='pay_action'),
    path('payreturn',views.payment_confo,name='payment_confo')
    


]

#Addding static files
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)