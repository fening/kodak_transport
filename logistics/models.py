from django.db import models
from django.contrib.auth.models import User

class TransportRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    po_number = models.CharField(max_length=100)
    location_from = models.CharField(max_length=200)
    location_to = models.CharField(max_length=200)
    dh_miles = models.FloatField()
    miles = models.FloatField()
    fuel = models.FloatField()
    food = models.FloatField()
    lumper = models.FloatField()
    pay = models.FloatField()

    def __str__(self):
        return f"{self.po_number} - {self.date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"