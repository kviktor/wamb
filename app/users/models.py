from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        user = self.model(email=email, username=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(
            email=email,
            username=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    email = models.EmailField(unique=True)

    objects = UserManager()
