from django.db import models


class Customer(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'покупатель'
        verbose_name_plural = 'покупатели'

    def __str__(self):
        return self.name