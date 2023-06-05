from django.db import models

class UploadedData(models.Model):
    reference_id = models.CharField(max_length=8, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=12)
    ename = models.CharField(max_length=100)

    def __str__(self):
        return self.reference_id

