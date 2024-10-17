from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
from django.db.models import Max

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
# create listing -> title, desc, bid, poster, watchlister, status,
@login_required
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]

        poster = request.user
        status = True
        # true means open

        picture = request.POST["picture"]

        listing = Listing(title=title, description=description, bid=bid, poster=poster, status=status, picture=picture)
        listing.save()

        return HttpResponseRedirect(reverse("listing", args=[listing.id]))
    else:
        return render(request, "auctions/create.html")

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    status = listing.status

    if request.user.is_authenticated:
        # status is true if bidding closed
        bidder = request.user
        bids = Bid.objects.filter(listing=listing)
        
        check = Watchlist.objects.filter(listing=listing_id, user=request.user)

        if check:
            in_watchlist=True
        else:
            in_watchlist=False

        # check if there is atleast one bid
        if bids:
            max_bid = bids.order_by('-price').first()
            # status true if still open
            if status == False: 
                highest_bidder = max_bid.bidder
                max_bid_value = max_bid.price
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "winner": highest_bidder,
                    "comments": Comment.objects.filter(listing=listing),
                    "watchlist": Watchlist.objects.filter(listing=listing_id),
                    "in_watchlist": in_watchlist,
                    "cur_val": max_bid_value,
                })
            else:
                max_bid_value = max_bid.price
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "winner": None,
                    "comments": Comment.objects.filter(listing=listing),
                    "watchlist": Watchlist.objects.filter(listing=listing_id),
                    "in_watchlist": in_watchlist,
                    "cur_val": max_bid_value
                })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": Comment.objects.filter(listing=listing),
                "watchlist": Watchlist.objects.filter(listing=listing_id),
                "in_watchlist": in_watchlist,
            })
    else:
        # not yet authenticated
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": Comment.objects.filter(listing=listing),
                "watchlist": Watchlist.objects.filter(listing=listing_id),
            })


# to create Bid you need bidder and price
# to access max price you need to filter all bids on this listing and get the maximum bid price

def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bidder = request.user
    price = float(request.POST["price"])

    bids=Bid.objects.filter(listing=listing)

    if bids:
        max_bid = bids.order_by('-price').first()
        if price > max_bid.price:
            # Place the bid
            bid = Bid(bidder=bidder, price=price, listing=listing)
            bid.save()
            return HttpResponseRedirect(reverse('result', args=[1]))  # Redirects to the 'results' view
        else:
            return HttpResponseRedirect(reverse('result', args=[0]))
    else:
        if price >= listing.bid:
            bid = Bid(bidder=bidder, price=price, listing=listing)
            bid.save()
            return HttpResponseRedirect(reverse('result', args=[1]))
        else:
            return HttpResponseRedirect(reverse('result', args=[0]))

def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comment = request.POST["comment"]
    user = request.user

    new_comment = Comment(commenter=user, comment=comment, listing=listing)
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def watchlist_add(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist = Watchlist(user=request.user, listing=listing)
    watchlist.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def watchlist_remove(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist = Watchlist.objects.filter(listing=listing).first()
    watchlist.delete()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def close(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.status = False
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def result(request, type):
    return render(request, "auctions/result.html", {
        "type": type
    })

def watchlist(request):
    list = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlists" : list
    })

def category(request, cat_name=None):
    if not cat_name:  
        return render(request, "auctions/category.html", {
            "categories": Category.objects.all()
        })
    else:
        try:
            cur_cat = Category.objects.get(name=cat_name)
            return render(request, "auctions/category.html", {
                "listings": cur_cat.listing.all(),
                "name": cur_cat.name
            })
        except Category.DoesNotExist:
            return render(request, "auctions/category.html", {
                "error": f"Category '{cat_name}' not found."
            })
