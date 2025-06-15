from django.db import models
from accounts.models import User
from datetime import date

class Book(models.Model):
    bookID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    available = models.BooleanField(default=True)
    penalty_until = models.DateField(null=True, blank=True)
    loan_count = models.PositiveIntegerField(default=0)

class Loan(models.Model):
    loanID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID', related_name='loans')
    bookID = models.ForeignKey(Book, null=True, on_delete=models.CASCADE, db_column='bookID')
    start_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)

class Reservation(models.Model):
    reservationID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    bookID = models.ForeignKey(Book, null=True, on_delete=models.CASCADE, db_column='bookID')
    reservation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
