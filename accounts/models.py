from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    HR_ADMIN = "hr_admin", "HR Admin"
    HR_MANAGER = "hr_manager", "HR Manager"
    MANAGER = "manager", "Department Manager"
    RECRUITER = "recruiter", "Recruiter"
    EMPLOYEE = "employee", "Employee"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        return full or self.username

    @property
    def is_hr_staff(self):
        return self.role in {
            UserRole.SUPER_ADMIN,
            UserRole.HR_ADMIN,
            UserRole.HR_MANAGER,
        }

    @property
    def is_manager_or_above(self):
        return self.role in {
            UserRole.SUPER_ADMIN,
            UserRole.HR_ADMIN,
            UserRole.HR_MANAGER,
            UserRole.MANAGER,
        }

    @property
    def can_recruit(self):
        return self.role in {
            UserRole.SUPER_ADMIN,
            UserRole.HR_ADMIN,
            UserRole.HR_MANAGER,
            UserRole.RECRUITER,
        }
