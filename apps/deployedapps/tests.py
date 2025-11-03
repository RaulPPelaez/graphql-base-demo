from django.test import TestCase
from apps.users.models import User, PlanChoices
from apps.deployedapps.models import DeployedApp


class DeployedAppModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(username="testuser", plan=PlanChoices.HOBBY)

    def test_app_creation(self):
        """Test creating a deployed app"""
        app = DeployedApp.objects.create(owner=self.user)

        self.assertEqual(app.owner, self.user)
        self.assertTrue(app.active)
        self.assertTrue(app.id.startswith("app_"))
        self.assertEqual(len(app.id), 20)  # app_ + 16 characters

    def test_app_id_format(self):
        """Test that app ID follows the correct format"""
        app = DeployedApp.objects.create(owner=self.user)
        self.assertTrue(app.id.startswith("app_"))
        id_part = app.id[4:]
        self.assertTrue(id_part.isalnum())

    def test_app_inactive(self):
        """Test creating an inactive app"""
        app = DeployedApp.objects.create(owner=self.user, active=False)
        self.assertFalse(app.active)

    def test_app_relationship_with_user(self):
        """Test the relationship between app and user"""
        app1 = DeployedApp.objects.create(owner=self.user)
        app2 = DeployedApp.objects.create(owner=self.user)
        self.assertEqual(self.user.apps.count(), 2)
        self.assertIn(app1, self.user.apps.all())
        self.assertIn(app2, self.user.apps.all())

    def test_app_cascade_delete(self):
        """Test that apps are deleted when user is deleted"""
        app = DeployedApp.objects.create(owner=self.user)
        app_id = app.id
        self.user.delete()
        self.assertFalse(DeployedApp.objects.filter(id=app_id).exists())

    def test_app_str_representation(self):
        """Test string representation of app"""
        app = DeployedApp.objects.create(owner=self.user)
        expected = f"App {app.id} (Owner: {self.user.username})"
        self.assertEqual(str(app), expected)
