from django.db import models
from django.contrib.auth.models import User

class TransportRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    po_number = models.CharField(max_length=100)
    location_from = models.CharField(max_length=255)
    location_to = models.CharField(max_length=255)
    dh_miles = models.DecimalField(max_digits=10, decimal_places=2)
    miles = models.DecimalField(max_digits=10, decimal_places=2)
    fuel = models.DecimalField(max_digits=10, decimal_places=2)
    food = models.DecimalField(max_digits=10, decimal_places=2)
    lumper = models.DecimalField(max_digits=10, decimal_places=2)
    pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.po_number} - {self.date}"