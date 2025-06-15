from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, student_id, username, phone, email, password=None):
        if not student_id:
            raise ValueError('학번은 필수입니다.')
        user = self.model(
            student_id=student_id,
            username=username,
            phone=phone,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, username, phone, email, password):
        user = self.create_user(student_id, username, phone, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser): # GRASP - Information Expert, Low Coupling
    student_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    penalty_until = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [
        ('allowed', '대여 가능'),
        ('banned', '대여 금지'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='allowed')
    objects = UserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['username', 'phone', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True

    @property
    def is_staff(self):
        return self.is_admin
