# Async Test

# from django.test import TestCase, AsyncClient
# from django.urls import reverse

# class AsyncExampleViewTestCase(TestCase):
#     async def test_async_example_view(self):
#         client = AsyncClient()
#         response = await client.get(reverse('async_example'))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {'message': 'Async operation complete'})



# Unit Test

# from django.test import TestCase
# from myapp.models import Product

# class ProductTestCase(TestCase):
#     def setUp(self):
#         Product.objects.create(name='Test Product', price=10.0)

#     def test_product_creation(self):
#         product = Product.objects.get(name='Test Product')
#         self.assertEqual(product.price, 10.0)



# Custom User Test

# from django.test import TestCase
# from .models import User

# class UserModelTestCase(TestCase):
#     def test_create_user(self):
#         user = User.objects.create_user(username='testuser', password='password')
#         self.assertEqual(user.username, 'testuser')
#         self.assertTrue(user.check_password('password'))



# Celery, Redis Test

# from unittest.mock import patch
# from celery.result import AsyncResult
# from myapp.tasks import process_data

# def test_process_data_task():
#     with patch('myapp.tasks.process_data.delay') as mock_process_data:
#         # Simulating task execution
#         mock_result = AsyncResult('mock_task_id')
#         mock_process_data.return_value = mock_result
#         task_result = process_data.delay('test data')
#         assert mock_process_data.called_once_with('test data')
#         assert task_result.id == 'mock_task_id'



# Docker Test

# from django.test import TestCase
# from django.contrib.auth.models import User
# from myapp.models import Product

# class ProductModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(username='testuser')
#         self.product = Product.objects.create(name='Test Product', price=10.0)

#     def test_product_name(self):
#         self.assertEqual(self.product.name, 'Test Product')

#     def test_product_price(self):
#         self.assertEqual(self.product.price, 10.0)

#     def test_product_like(self):
#         self.product.like.add(self.user)
#         self.assertIn(self.user, self.product.like.all())



# # Postgresql Test

# from django.test import TestCase
# from myapp.models import Product
# from decimal import Decimal

# class ProductModelTest(TestCase):
#     def setUp(self):
#         self.product = Product.objects.create(name="Test Product", price=Decimal('10.99'))

#     def test_product_creation(self):
#         product = Product.objects.get(name="Test Product")
#         self.assertEqual(product.price, Decimal('10.99'))
#         self.assertEqual(product.name, "Test Product")

#     def tearDown(self):
#         self.product.delete()