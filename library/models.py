from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    student_id = models.IntegerField(unique=True)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    @property
    def is_overdue(self):
        return self.return_date is None and self.due_date < date.today()

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reservation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
