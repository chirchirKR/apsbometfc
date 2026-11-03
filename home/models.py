from django.db import models
from django.contrib.auth.models import User

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