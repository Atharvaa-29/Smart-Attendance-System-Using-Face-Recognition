from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib import admin


class FacultyManager(BaseUserManager):
    def create_user(self, name, password=None):
        if not name:
            raise ValueError("The Name field must be set")
        user = self.model(name=name)
        user.set_password(password)  # Use Django's password hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None):
        user = self.create_user(name, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Faculty(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50, unique=True)  # Ensure usernames are unique
    key = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_active = models.BooleanField(default=True)  # If the user is active

    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = []  # Any additional fields required for the user creation

    # Adding related names to avoid clashes
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="faculty_groups",  # Change to a unique related name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="faculty_user_permissions",  # Change to a unique related name
        blank=True,
    )

    objects = FacultyManager()

    def __str__(self):
        return self.name


# Other models remain the same...


class Student(models.Model):
    roll_no = models.CharField(max_length=9, null=False, blank=False, primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=128)  # Change to 128 for hashed passwords

    def __str__(self):
        return self.name


class Degree(models.Model):
    degree = models.CharField(max_length=50)  # Increase max_length for flexibility
    years = models.CharField(max_length=50)
    branches = models.CharField(max_length=50)

    def __str__(self):
        return self.degree


class Course(models.Model):
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    degree = models.ForeignKey(
        Degree, on_delete=models.CASCADE
    )  # Use ForeignKey for relationship
    students = models.ManyToManyField(
        Student, related_name="courses"
    )  # Use plural for clarity

    def __str__(self):
        return self.course
