
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NomNom.settings')
django.setup()

from pastry.models import Pastry

# Clear existing standard pastries
print("Clearing existing standard pastries...")
Pastry.objects.filter(is_custom=False).delete()

# Define products from views.py
products_data = {
    'CAKE': [
        {'name': 'Vanilla', 'price': 1000, 'image': 'images/vanilla_cake.png'},
        {'name': 'Cheesecake', 'price': 750, 'image': 'images/cheese_cake.png'},
        {'name': 'Mint', 'price': 500, 'image': 'images/mint_cake.png'},
        {'name': 'Chocolate', 'price': 1750, 'image': 'images/chocolate_cake.png'},
        {'name': 'Fudgy McFudgecake', 'price': 1250, 'image': 'landing/images/fudgy.png'},
    ],
    'BROWNIE': [
        {'name': 'Strawberry', 'price': 500, 'image': 'images/strawberry_brownie.png'},
        {'name': 'Chocolate', 'price': 750, 'image': 'images/chocolate_brownie.png'},
        {'name': 'Rasberry', 'price': 850, 'image': 'images/rasberry_brownie.png'},
        {'name': 'Vanilla', 'price': 600, 'image': 'images/vanilla_brownie.png'},
    ],
    'CUPCAKE': [
        {'name': 'Rasberry', 'price': 450, 'image': 'images/rasberry_cupcake.png'},
        {'name': 'Chocolate', 'price': 900, 'image': 'images/chocolate_cupcake.png'},
        {'name': 'Oreo', 'price': 500, 'image': 'images/oreo_cupcake.png'},
        {'name': 'Strawberry', 'price': 600, 'image': 'images/strawberry_cupcake.png'},
    ],
    'COOKIE': [
        {'name': 'Chocolate Chip', 'price': 450, 'image': 'images/chocolatechip_cookie.png'},
        {'name': 'Oat', 'price': 400, 'image': 'images/oat_cookie.png'},
        {'name': 'Fruit', 'price': 500, 'image': 'images/fruit_cookie.png'},
        {'name': 'Smarties', 'price': 425, 'image': 'images/smarties_cookie.png'},
    ],
    'DONUT': [
        {'name': 'Strawberry', 'price': 400, 'image': 'images/strawberry_donut.png'},
        {'name': 'Chocolate', 'price': 450, 'image': 'images/chocolate_donut.png'},
        {'name': 'Vanilla', 'price': 425, 'image': 'images/vanilla_donut.png'},
        {'name': 'Cinnamon Sugar', 'price': 350, 'image': 'images/cinnamonsugar_donut.png'},
    ],
    'TART': [
        {'name': 'Cranberry', 'price': 450, 'image': 'images/cranberry_tart.png'},
        {'name': 'Vanilla', 'price': 375, 'image': 'images/vanilla_tart.png'},
        {'name': 'Red Fruits', 'price': 400, 'image': 'images/redfruit_tart.png'},
        {'name': 'Banana', 'price': 350, 'image': 'images/banana_tart.png'},
    ]
}

for category, items in products_data.items():
    for item in items:
        Pastry.objects.create(
            pastry_name=item['name'],
            pastry_category=category,
            pastry_price=item['price'],
            image=item['image'],
            is_custom=False,
            is_available=True
        )
        print(f"Created: {item['name']} ({category})")