from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing',blank=True,related_name="follower",null=True)
    def __str__(self) :
        return f'{self.username}'

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    start_bidding = models.FloatField()
    image = models.ImageField(blank=True,upload_to='images/',null= True)
    owner = models.ForeignKey(User,related_name='sale_item',on_delete=models.CASCADE)
    is_close = models.BooleanField()
    buyer = models.ForeignKey(User,null= True,blank=True,related_name="get_item",on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True,blank=True)
    def __str__(self) :
        if self.buyer is not None:
            return f'{self.title}({self.owner})->({self.buyer})'
        return f'{self.title}({self.owner})'

class Bid(models.Model):
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name="biddings")
    bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="biddings")
    price = models.FloatField()
    is_highest = models.ForeignKey(Listing,blank=True,null=True,related_name="highest_bidding",on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True,blank=True)
    def __str__(self) :
        return f'${self.price} by {self.bidder}'
    
class Comment(models.Model):
    content = models.CharField(max_length=128)
    person = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    comment_item = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="comments")
    datetime = models.DateTimeField(null=True,blank=True)
    def __str__(self) :
        return f'{self.person}: {self.content}'
    
class Category(models.Model):
    category = models.CharField(max_length=16)
    category_item = models.ManyToManyField(Listing,related_name='category',blank=True,null=True)
    def __str__(self) :
        num = self.category_item.count()
        return f'{self.category} (number:{num})'