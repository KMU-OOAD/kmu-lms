from django.contrib import admin
from .models import Book, Loan, Reservation

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'available')
    search_fields = ('title', 'author')
    list_filter = ('available',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'start_date', 'due_date', 'return_date')
    list_filter = ('start_date', 'return_date')
    search_fields = ('book__title', 'user__username')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reservation_date', 'status')
    list_filter = ('status', 'reservation_date')
    search_fields = ('book__title', 'user__username')
