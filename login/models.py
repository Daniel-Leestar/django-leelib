from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)  # 它不会明文存储密码，而是对密码进行哈希（加密）处理，然后再存入数据库。
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    privilege = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # 用于区分管理用户
    is_superuser = models.BooleanField(default=False)  # 用于超级管理员权限

    USERNAME_FIELD = 'email'  # 使用 email 作为用户名字段
    REQUIRED_FIELDS = ['first_name', 'last_name']  # 必填字段

    objects = UserManager()  # 为 User 类绑定自定义的 Manager

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
