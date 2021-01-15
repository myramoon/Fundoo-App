from django.db import models
from accountmanagement.models import Account

class Label(models.Model):
    name = models.CharField(max_length = 130, null = False , unique = True , blank=False)
    is_deleted = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.save()

