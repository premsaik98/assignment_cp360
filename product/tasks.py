from celery import shared_task
from .models import Product
from django.contrib.auth.models import User
from faker import Faker
import random

fake = Faker()

@shared_task
def generate_dummy_products(count):
    users = list(User.objects.all())
    for _ in range(count):
        uploaded_by = random.choice(users) if users else None
        Product.objects.create(
            title=fake.name(),
            description=fake.text(),
            price=fake.random_number(digits=5),
            status='pending',
            uploaded_by=uploaded_by
        )
    return f'{count} dummy products generated successfully.'
