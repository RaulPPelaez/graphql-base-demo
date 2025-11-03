from django.core.management.base import BaseCommand
from apps.users.models import User, PlanChoices
from apps.deployedapps.models import DeployedApp


class Command(BaseCommand):
    help = "Create fixtures with test users and apps"

    def handle(self, *args, **options):
        self.stdout.write("Creating fixtures...")
        DeployedApp.objects.all().delete()
        User.objects.all().delete()
        hobby_users = []
        for i in range(1, 4):
            user = User.objects.create(
                username=f"hobby_user_{i}", plan=PlanChoices.HOBBY
            )
            hobby_users.append(user)
            self.stdout.write(f"Created hobby user: {user.username} (ID: {user.id})")

        pro_users = []
        for i in range(1, 4):
            user = User.objects.create(username=f"pro_user_{i}", plan=PlanChoices.PRO)
            pro_users.append(user)
            self.stdout.write(f"Created pro user: {user.username} (ID: {user.id})")

        app_count = 0
        for user in hobby_users:
            for i in range(2):
                app = DeployedApp.objects.create(
                    owner=user, active=i == 0  # First app active, second inactive
                )
                app_count += 1
                self.stdout.write(f"Created app {app.id} for {user.username}")

        for idx, user in enumerate(pro_users):
            num_apps = 3 + (idx % 3)
            for i in range(num_apps):
                app = DeployedApp.objects.create(owner=user, active=True)
                app_count += 1
                self.stdout.write(f"Created app {app.id} for {user.username}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {len(hobby_users)} hobby users, "
                f"{len(pro_users)} pro users, and {app_count} apps"
            )
        )
