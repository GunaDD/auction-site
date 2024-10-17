from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    bid = models.IntegerField()
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="your_listings", null=True)
    status = models.BooleanField()
    picture = models.URLField()

    def __str__(self):
        return f"{self.title} by {self.poster.username}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="your_bids")
    price = models.FloatField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_list")

    def __str__(self):
        return f"bid by {self.bidder.username} at price {self.price} on {self.listing.title}"

class Category(models.Model):
    name = models.CharField(max_length=64)
    listing = models.ManyToManyField(Listing, blank=True, related_name="your_categories")

    def __str__(self):
        return f"category {self.name}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="your_watchlist", null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_watchlister", null=True)

    def __str__(self):
        return f"watchlist by {self.user.username} on {self.listing.title}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="your_comments_list")
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"comment  by {self.commenter.username} on {self.listing.title}"