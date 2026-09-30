from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(self, email, password):
        user = self.model(email=email, username=email, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    email = models.EmailField(unique=True)

    objects = UserManager()
