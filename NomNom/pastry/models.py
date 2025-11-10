from django.db import models

class Pastry(models.Model):
    PASTRY_TYPES = [
    ('CAKE', 'Cake'),
    ('BROWNIE', 'Brownie'),
    ('DOUGHNUT', 'Doughnut'),
    ('COOKIE', 'Cookie'),
    ('TART', 'Tart'),
    ('CUPCAKE', 'Cupcake'),
]
    pastry_name = models.CharField(max_length=100)
    pastry_price = models.DecimalField(max_digits=8, decimal_places=2)
    pastry_category = models.CharField(max_length=20, choices=PASTRY_TYPES, editable=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Pastries"

    def __str__(self):
        return self.name
