from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Category, WatchList
from .forms import CreateListingForm

@login_required
def index(request):
    return render(request, "auctions/index.html", 
    {"listings": Listing.objects.filter(sold=False)
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

@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["price"]
            image_url = form.cleaned_data["image_url"]
            user = request.user
            category_id, created = Category.objects.get_or_create(category=request.POST["categories"])
            Listing.objects.create(user = user, title = title, description = description, 
            price = bid, image_url = image_url, category = category_id)
    
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/create.html", {
            "listing_form": CreateListingForm(),
            "categories": Category.objects.all()
        })

@login_required
def listing_info(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    is_owner = True if listing.user == user else False
    category = Category.objects.get(category=listing.category)
    comments = Comment.objects.filter(listing=listing.id)
    watching = WatchList.objects.filter(user = user, listing = listing)
    if watching:
        watching = WatchList.objects.get(user = user, listing = listing)

    return listing, user, is_owner, category, comments, watching

@login_required
def listing(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watching = info[0], info[1], info[2], info[3], info[4], info[5]
    if request.method == "POST":
        comment = request.POST["comment"]
        if comment != "":
            Comment.objects.create(user = user, listing = listing, comment = comment)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": WatchList.objects.filter(user = user, watching=True),
        "is_owner": is_owner
    })

@login_required
def remove_watchlist(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    #watch = watch.first()  # Get the first (and only) item from the QuerySet
    if watch:  # Check if an item was returned
        watch.watching = False
        watch.save()

    try:
        watching = WatchList.objects.get(user = user, listing = listing).watching
    except WatchList.DoesNotExist:
        watching = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watching, 
        "is_owner": is_owner
    })

@login_required
def add_watchlist(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]
    watch = WatchList.objects.filter(user = user, listing = listing)
    if watch:
        watch = WatchList.objects.get(user = user, listing = listing)
        watch.watching = True
        watch.save()
    else:
        WatchList.objects.create(user = user, listing = listing, watching = True)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": WatchList.objects.get(user = user, listing = listing).watching, 
        "is_owner": is_owner
    })

@login_required
def bidding(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    if request.method == "POST":
        bid = request.POST["bid"]
        listing.price = bid
        listing.save()
        Bid.objects.create(user = user, price = bid, listing = listing)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "is_owner": is_owner
    })

@login_required
def close_bidding(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    listing.sold = True
    winner = Bid.objects.get(price = listing.price, listing = listing).user
    listing.winner = winner  # Set the winner of the listing
    listing.save()
    print(user.id, winner.id)
    is_winner = user.id == winner.id

    return render(request, "auctions/close_bidding.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "is_owner": is_owner,
        "is_winner": is_winner
    })

def category(request, category):
    category_obj = Category.objects.get(category=category)
    listings = Listing.objects.filter(category=category_obj, sold=False)
    return render(request, "auctions/categories.html", {
        "listings": listings,
        "category": category
    })
@login_required
def watchlist(request):
    user = request.user
    watchlist_items = WatchList.objects.filter(user=user, watching=True)
    listings = [item.listing for item in watchlist_items if item.listing.sold == False]
    return render(request, "auctions/watchlist.html", {"listings": listings})