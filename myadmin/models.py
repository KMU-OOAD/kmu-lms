# from django.db import models
# from django.contrib.auth.models import AbstractUser
#
#
# # Create your models here.
# class User(AbstractUser):
#     can_borrow = models.BooleanField(default=True)
#     penalty_until = models.DateField(null=True, blank=True)
#
# class Book(models.Model):
#     bookID = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=200)
#     author = models.CharField(max_length=100)
#     status = models.CharField(max_length=50, default='available')
#     loan_count = models.IntegerField(default=0)
#
# class Loan(models.Model):
#     loanID = models.AutoField(primary_key=True)
#     startDate = models.DateField()
#     dueDate = models.DateField()
#     returnDate = models.DateField(null=True, blank=True)
#     is_overdue = models.BooleanField(default=False)
#     userID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
#     bookID = models.ForeignKey(Book, null=True, on_delete=models.CASCADE, db_column='bookID')
#
# class Reservation(models.Model):
#     reservationID = models.AutoField(primary_key=True)
#     reservationDate = models.DateField()
#     status = models.CharField(max_length=20, default='Pending')
#     userID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
#
# class Notice(models.Model):
#     noticeID = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     postedDate = models.DateField()
#
# class LibraryInfo(models.Model):
#     infoId = models.AutoField(primary_key=True)
#     day = models.CharField(max_length=20)
#     openTime = models.TimeField()
#     closeTime = models.TimeField()