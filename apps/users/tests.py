from django.test import TestCase
from apps.users.models import User, PlanChoices


class UserModelTest(TestCase):
    def test_user_creation(self):
        """Test creating a user with default values"""
        user = User.objects.create(username="testuser")

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.plan, PlanChoices.HOBBY)
        self.assertTrue(user.id.startswith("u_"))
        self.assertEqual(len(user.id), 18)  # u_ + 16 characters

    def test_user_id_format(self):
        """Test that user ID follows the correct format"""
        user = User.objects.create(username="testuser2")
        self.assertTrue(user.id.startswith("u_"))
        id_part = user.id[2:]
        self.assertTrue(id_part.isalnum())

    def test_user_with_pro_plan(self):
        """Test creating a user with Pro plan"""
        user = User.objects.create(username="prouser", plan=PlanChoices.PRO)
        self.assertEqual(user.plan, PlanChoices.PRO)

    def test_user_unique_username(self):
        """Test that usernames must be unique"""
        User.objects.create(username="duplicate")
        with self.assertRaises(Exception):
            User.objects.create(username="duplicate")

    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create(username="testuser", plan=PlanChoices.PRO)
        self.assertEqual(str(user), "testuser (PRO)")
