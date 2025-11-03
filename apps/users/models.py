from django.db import models
import secrets
import string


def generate_user_id():
    return f"u_{''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))}"


class PlanChoices(models.TextChoices):
    HOBBY = "HOBBY", "Hobby"
    PRO = "PRO", "Pro"


class User(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_user_id, editable=False
    )
    username = models.CharField(max_length=150, unique=True)
    plan = models.CharField(
        max_length=10, choices=PlanChoices.choices, default=PlanChoices.HOBBY
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.plan})"
