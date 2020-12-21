from django.db import models

class Label(models.Model):
    name = models.CharField(max_length = 130, null = True , unique = True)
    is_deleted = models.BooleanField(default = False)

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.save()  