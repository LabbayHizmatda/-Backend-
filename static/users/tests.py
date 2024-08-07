from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import *

class CustomUserModelCreateTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "user_id": 12321,
            "first_name": "string",
            "last_name": "string",
            "password": "admin",
            "phone_number": "+99898",
            "birth_date": "2024-08-06",
            "language": "Uzbek",
            "roles": [
                "Worker"
            ]
        }

    def test_register_user(self):
        response = self.client.post(reverse('register'), self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().user_id, self.user_data['user_id'])
    
    