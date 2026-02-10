
from django.shortcuts import render,redirect
from .util import get_phonepe_client, meta_info_generation,buil_request
import os
from uuid import uuid4

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Book_details


# def home(request):
#     books = Book_details.objects.all()

#     # use local placeholder stored in static/images/
#     placeholder_image = "images/placeholder.png"

#     return render(request, "home.html", {
#         "books": books,
#         "placeholder": placeholder_image,
#     })

def home(request):
    books = Book_details.objects.all()

    # Local placeholder stored in static/images/
    placeholder_image = "images/placeholder.png"

    # Last 5 new arrivals (latest added books)
    new_arrivals = Book_details.objects.order_by('-id')[:5]

    return render(request, "common/home.html", {
        "books": books,
        "placeholder": placeholder_image,
        "new_arrivals": new_arrivals,
    })





def paypage(request):
    return render(request, 'payment.html')

def payment_send(request):
    unique_order_id = str(uuid4())
    amount_paisa = request.POST.get('amount')
    amount_rupees = int(amount_paisa) * 100
    client = get_phonepe_client()
    meta_info = meta_info_generation()
    redirect_url = request.build_absolute_uri(
        reverse("payment_confo")
    )
    payrequest = buil_request(client,unique_order_id,amount_rupees,redirect_url,meta_info)
    standard_pay_response = client.pay(payrequest)
    request.session["last_order_id"]= unique_order_id
    checkout_page_url = standard_pay_response.redirect_url
    return redirect(checkout_page_url)

def payment_confo(request):
    merchant_order_id= request.session.get("last_order_id")
    if not merchant_order_id:
        return HttpResponse("No order ID found in session", status=400)
    
    client = get_phonepe_client()
    status = client.get_order_status(merchant_order_id)
    
    return HttpResponse(
        f"Return from PhonePe.<br>"
        f"Order: {merchant_order_id}<br>"
        f"Status: {status.state}<br>"
        f"Amount: {status.amount/100}"
    )







