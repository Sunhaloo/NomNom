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

    # Pastry basic model - Predefined for filtered pastries BUT blank for pastries created through cake customisation page
    pastry_name = models.CharField(max_length=100)
    pastry_category = models.CharField(max_length=20, choices=PASTRY_TYPES)
    pastry_price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='pastries/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    # Customisation attributes - Predefined for filtered pastries BUT blank for pastries created through cake customisation page
    flavour = models.CharField(max_length=50, blank=True, null=True)
    filling = models.CharField(max_length=50, blank=True, null=True)
    frosting = models.CharField(max_length=50, blank=True, null=True)
    decoration = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=150, blank=True, null=True)
    size = models.CharField(
        max_length=20,
        choices=[
            ('S', 'Small'),
            ('M', 'Medium'),
            ('L', 'Large'),
            ('XL', 'Extra Large'),
        ],
        blank=True, null=True
    )

    # To identify between customized and predefined pastry
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        label = "Custom" if self.is_custom else "Preset"
        return f"{label} {self.pastry_category} - {self.pastry_name}"
