from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'покупатель'
        verbose_name_plural = 'покупатели'

    def __str__(self):
        return self.name