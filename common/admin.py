from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book_details
@admin.register(Book_details)
class BookDetailsAdmin(admin.ModelAdmin):
    list_display = ('Book_name', 'Authors_name', 'ISBN', 'Available_books')
    search_fields = ('Book_name', 'Authors_name', 'ISBN')

