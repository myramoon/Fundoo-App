from django.db import models

# Create your models here.



class Label(models.Model):
    name = models.CharField(max_length = 130, null = True , unique = True)

    def __str__(self):
        return self.name