from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Match(models.Model):
    home_team = models.CharField(max_length=30)
    away_team = models.CharField(max_length=30)
    stadium = models.CharField(max_length=40)
    county = models.CharField(max_length=30)
    datetime_played = models.DateTimeField()
    homelogo = models.ImageField(upload_to="media/")
    awaylogo = models.ImageField(upload_to="media/")
    
    def __str__(self):
        return f"{self.home_team.upper()} VS {self.away_team.upper()}"
        
    def homeTcaseUp(self):
        return self.home_team.upper()
        
    def awayTcaseUp(self):
        return self.away_team.upper()
        
class Result(models.Model):
    home_team = models.CharField(max_length=30)
    away_team = models.CharField(max_length=30)
    stadium = models.CharField(max_length=40)
    county = models.CharField(max_length=30)
    datetime_played = models.DateTimeField()
    home_score = models.PositiveIntegerField()
    away_score = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.home_team.upper()} VS {self.away_team.upper()}"

class Product(models.Model):
    data_product = models.CharField(max_length=30)
    data_price = models.PositiveIntegerField()
    img_src = models.ImageField(upload_to="media/")
    data_details = models.TextField()
    sizes = models.CharField()

    def __str__(self):
        return self.data_product.upper()

    def splitSize(self):
        return self.sizes.split(',')
        
class News(models.Model):
    title = models.CharField(max_length=101)
    img_src = models.ImageField(upload_to="media/")
    content = models.TextField()
    date_edited = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title.upper()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)       
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sized = models.CharField(max_length=4)
    payed = models.DecimalField(decimal_places=2, max_digits=10)
    phone_number = models.PositiveIntegerField()
    date_payed = models.DateTimeField(auto_now_add=True)
    
User = get_user_model()


class PasswordResetToken(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    used_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def is_valid(self):
        return (
            self.used_at is None
            and timezone.now() < self.expires_at
            and self.user.is_active
        )

    def __str__(self):
        return f"Password reset for {self.user.username}"
    