from django.shortcuts import render, redirect, HttpResponse
from common.models import Registration
from common.forms import Registrationform, Reservationform

def home(request):
    return render(request, 'adminhome.html')