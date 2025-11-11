from django.db import models

#Parent model
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
        return self.pastry_name
    
#2nd parent model - inherits from pastry if customer chooses to customize a pastry 
class PastryCustomisation(models.Model):
    pastry = models.OneToOneField(Pastry, on_delete=models.CASCADE, related_name='customisation')   
    flavour = models.CharField(max_length=50)
    filling = models.CharField(max_length=50, blank=True)
    frosting = models.CharField(max_length=50, blank=True)
    layers = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, choices=[
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ])
    decoration = models.CharField(max_length=100, blank=True)
    message = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Cake Customisation for {self.pastry.name} ({self.flavour}, {self.size})"

#children classes for each category of pastry - inherits from grandparent(pastry) and parent(cakecustomisation)
# customisation for cakes
class CakeCustomisation(PastryCustomisation):
    pass 
  
#customisation for brownies
class BrownieCustomisation(PastryCustomisation):
    chocolate_type = models.CharField(
        max_length=20,
        choices=[('DARK', 'Dark Chocolate'), ('MILK', 'Milk Chocolate')],
        default='DARK'
    )

    texture = models.CharField(
        max_length=20,
        choices=[('FUDGY', 'Fudgy'), ('CAKEY', 'Cakey')],
        default='FUDGY'
    )    
    toppings = models.CharField(max_length=100, blank=True)

    box_size = models.CharField(
    max_length=20,
    choices=[
        ('S', 'Small (4 pieces)'),
        ('M', 'Medium (8 pieces)'),
        ('L', 'Large (12 pieces)'),
        ('BOX', 'Box of 24'),
    ],
    default='M',        
    blank=True, null=True  
)
    custom_message = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.flavour:
            self.flavour = "Chocolate"
        super().save(*args, **kwargs)


#customisation for cookies
class CookieCustomisation(PastryCustomisation):
    chips = models.CharField(
        max_length=30,
        choices=[('CHOCOLATE', 'Chocolate Chips'), ('FRUIT', 'Fruit Bits'), ('NUTS', 'Nuts')],
        default='CHOCOLATE'
    )
    dough_type = models.CharField(max_length=50, choices=[
        ('CHOCOLATE', 'Chocolate'),
        ('OAT', 'Oat'),
        ('FRUIT', 'Fruit'),
        ('PEANUT', 'Peanut Butter'),
    ])
    pack_size = models.CharField(max_length=20, choices=[
        ('S', 'Small (6 cookies)'),
        ('M', 'Medium (12 cookies)'),
        ('L', 'Large (24 cookies)'),
    ])

#customisation for doughnut
class DoughnutCustomisation(PastryCustomisation):
    dough_flavour = models.CharField(max_length=50, choices=[
        ('VANILLA', 'Vanilla'),
        ('CHOCOLATE', 'Chocolate'),
        ('STRAWBERRY', 'Strawberry'),
    ])
    glaze = models.CharField(max_length=50, choices=[
        ('NONE', 'No Glaze'),
        ('SUGAR', 'Sugar Glaze'),
        ('CHOCOLATE', 'Chocolate Glaze'),
        ('CARAMEL', 'Caramel Glaze'),
    ])
    quantity = models.PositiveIntegerField(default=1)

#customisation for cupcakes

class CupcakeCustomisation(PastryCustomisation):
    icing_style = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)

#customisation for tart
class TartCustomisation(PastryCustomisation):
    filling_type = models.CharField(
        max_length=50,
        choices=[('FRUIT','Fruit'), ('CUSTARD','Custard'), ('CHOCOLATE', 'Chocolate Filling')],
        default='FRUIT'
    )
    fruit_choice = models.CharField(
        max_length=30,
        choices=[
            ('STRAWBERRY','Strawberry'),
            ('LEMON','Lemon'),
            ('MANGO','Mango'),
            ('BLUEBERRY','Blueberry'),
        ],
        default='STRAWBERRY',
        blank=True, null=True
    )
    crust_type = models.CharField(max_length=50, choices=[
        ('BUTTER', 'Butter Crust'),
        ('ALMOND', 'Almond Crust'),
        ('CHOCOLATE', 'Chocolate Crust'),
    ])
    serving = models.CharField(max_length=20, choices=[
        ('S', 'Mini (1 serving)'),
        ('M', 'Medium (2-3 servings)'),
        ('L', 'Large (5 servings)'),
    ])

