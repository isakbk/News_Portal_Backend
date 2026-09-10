from django.test import TestCase

from .serializers import EmployeeRegistrationSerializer

class EmployeeRegistrationSerializerTests(TestCase):
	def test_registration_creates_regular_employee_user(self):
		serializer = EmployeeRegistrationSerializer(
			data={
				"username": "reporter1",
				"email": "reporter1@example.com",
				"full_name": "News Reporter",
				"password": "strong-password-123",
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		profile = serializer.save()
		user = profile.user

		self.assertFalse(user.is_staff)
		self.assertFalse(user.is_superuser)
		self.assertTrue(user.check_password("strong-password-123"))
