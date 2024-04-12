from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required
from django import forms
import datetime
from django.core.validators import MinValueValidator


class create_form(forms.Form):
    title = forms.CharField(label='title',min_length=1,max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    start_bidding = forms.FloatField(label='start_bidding', validators=[MinValueValidator(0.0)], widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='description',max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(label='category',max_length=16,min_length=1,required=False, widget=forms.TextInput(attrs={'placeholder': 'optional','class': 'form-control'}))
    image = forms.ImageField(label='image(optional)',required=False)


class comment_form(forms.Form):
    content = forms.CharField(label=False,min_length=1,max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Enter your comment.','class': 'form-control'}))
    
    
class bid_form(forms.Form):
    content = forms.FloatField(label=False,validators=[MinValueValidator(0.0)],widget=forms.TextInput(attrs={'placeholder': 'Enter your bidding.','class': 'form-control'}))


def index(request):
    return render(request, "auctions/index.html",{"listings":Listing.objects.filter(is_close=False)})


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
def create(request):
    if request.method == "POST":
        form = create_form(request.POST,request.FILES)
        if form.is_valid():
            new_listing = Listing(
                title=form.cleaned_data["title"],
                start_bidding=form.cleaned_data["start_bidding"],
                description=form.cleaned_data["description"],
                image=form.cleaned_data.get("image"),
                owner = request.user,
                is_close = False,
                datetime = datetime.datetime.now()
            )
            new_listing.save()
            category = form.cleaned_data.get('category','')
            if category is not '':
                category=category.upper()
                try:
                    pick_category=Category.objects.get(category=category)
                    pick_category.category_item.add(new_listing)
                except Category.DoesNotExist:
                    new_cateory = Category.objects.create(category=category)
                    new_cateory.category_item.add(new_listing)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request,"auctions/create.html",{'form':form})
      
    return render(request, "auctions/create.html",{'form':create_form()})


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request,"auctions/watchlist.html",{"listings":listings})


def categories(request):
    categories = Category.objects.all()
    return render(request,"auctions/categories.html",{"categories":categories})


def categories2(request,category):
    try:
        category = category.upper()
        pick = Category.objects.get(category=category)
        listings = pick.category_item.all()
        return render(request,"auctions/categories2.html",{"listings":listings,"category":category})
    except Category.DoesNotExist:
            return HttpResponseNotFound()
        
        
def listings(request,listing_id):
    try:
        pick_listing = Listing.objects.get(pk=listing_id)
        comments = pick_listing.comments.all()
        biddings = pick_listing.biddings.all()
        is_follow = request.user.watchlist.filter(pk=pick_listing.id).exists()
        return render(request,"auctions/listings.html",{"pick_listing":pick_listing,"comments":comments,"biddings":biddings,"comment_form":comment_form(),"bid_form":bid_form(),"is_follow":is_follow})
    except Listing.DoesNotExist:
        return HttpResponseNotFound()
    
@login_required
def comment(request):
    if request.method == "POST":
        form = comment_form(request.POST)
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            if form.is_valid():
                new_comment = Comment(content=form.cleaned_data["content"],
                    person=request.user,
                    comment_item=pick_listing,
                    datetime=datetime.datetime.now()
                )
                new_comment.save()
                return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
            comments = pick_listing.comments.all()
            biddings = pick_listing.biddings.all()
            is_follow = request.user.watchlist.filter(pk=pick_listing.id).exists()
            return render(request,"auctions/listings.html",{"pick_listing":pick_listing,"comments":comments,"biddings":biddings,"comment_form":form,"bid_form":bid_form(),"is_follow":is_follow})
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()

@login_required
def bid(request):
    if request.method == "POST":
        form = bid_form(request.POST)
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            if form.is_valid():
                new_price = form.cleaned_data["content"]
                if pick_listing.highest_bidding.exists():
                    old_bid = pick_listing.highest_bidding.get()
                    if new_price > old_bid.price:
                        old_bid.is_highest=None
                        old_bid.save()
                    else:
                        comments = pick_listing.comments.all()
                        biddings = pick_listing.biddings.all()
                        is_follow = request.user.watchlist.filter(pk=pick_listing.id).exists()
                        return render(request,"auctions/listings.html",{"pick_listing":pick_listing,"comments":comments,"biddings":biddings,"comment_form":comment_form(),"bid_form":form,"message":"不得低于当前最高报价。","is_follow":is_follow})
                new_bid = Bid(price=new_price,
                    bidder=request.user,
                    bid_item=pick_listing,
                    is_highest=pick_listing,
                    datetime=datetime.datetime.now()
                )
                new_bid.save()
                return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
            comments = pick_listing.comments.all()
            biddings = pick_listing.biddings.all()
            is_follow = request.user.watchlist.filter(pk=pick_listing.id).exists()
            return render(request,"auctions/listings.html",{"pick_listing":pick_listing,"comments":comments,"biddings":biddings,"comment_form":comment_form(),"bid_form":form,"is_follow":is_follow})
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()


@login_required
def close(request):
    if request.method == "POST":
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            pick_listing.is_close = True
            pick_listing.save()
            if pick_listing.highest_bidding.exists():
                pick_bid = pick_listing.highest_bidding.get()
                buyer = pick_bid.bidder
                pick_listing.buyer=buyer
                pick_listing.save()
            return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()


@login_required
def open(request):
    if request.method == "POST":
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            pick_listing.is_close = False
            pick_listing.buyer=None
            pick_listing.save()
            return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()

@login_required
def follow(request):
    if request.method == "POST":
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            request.user.watchlist.add(pick_listing)
            return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()

@login_required
def unfollow(request):
    if request.method == "POST":
        listing_id = request.POST.get("id")
        try:
            pick_listing = Listing.objects.get(pk=listing_id)
            request.user.watchlist.remove(pick_listing)
            return HttpResponseRedirect(reverse("listings",kwargs={'listing_id': listing_id}))
        except Listing.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseNotFound()