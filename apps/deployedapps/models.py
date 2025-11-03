from django.db import models
import secrets
import string


def generate_app_id():
    return f"app_{''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))}"


class DeployedApp(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=generate_app_id, editable=False)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='apps')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deployed_apps'
        ordering = ['-created_at']

    def __str__(self):
        return f"App {self.id} (Owner: {self.owner.username})"
