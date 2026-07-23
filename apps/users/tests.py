"""
Smoke tests — prove auth + tool listing work.
Run:  python manage.py test
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.tools.models import Category
from apps.users.models import User


class AuthAndToolsSmokeTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Power Tools',
            slug='power-tools',
            description='Drills and saws',
        )

    def test_register_login_and_list_tool(self):
        # Register
        res = self.client.post(
            '/api/auth/register/',
            {
                'email': 'lender@example.com',
                'password': 'StrongPass123!',
                'full_name': 'Len Der',
                'neighborhood': 'Westlands',
                'role': 'lender',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Login
        res = self.client.post(
            '/api/auth/login/',
            {'email': 'lender@example.com', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Create tool
        res = self.client.post(
            '/api/tools/',
            {
                'title': 'Cordless Drill',
                'description': '18V drill with two batteries',
                'category': self.category.id,
                'condition': 'good',
                'daily_fee': '5.00',
                'neighborhood': 'Westlands',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Browse tools
        res = self.client.get('/api/tools/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data['count'], 1)
