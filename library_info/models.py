# library_info/models.py
from django.db import models

DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

DAY_ORDER = {
        'Mon': 1,
        'Tue': 2,
        'Wed': 3,
        'Thu': 4,
        'Fri': 5,
        'Sat': 6,
        'Sun': 7,
    }

class LibraryInfo(models.Model):
    day = models.CharField(max_length=10, choices=DAY_CHOICES, unique=True)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f'{self.get_day_display()} 운영 시간: {self.open_time} ~ {self.close_time}'

    @property
    def day_order(self):
        return DAY_ORDER.get(self.day, 99)  # 예외 처리용 디폴트