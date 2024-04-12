from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.create,name = "create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories",views.categories,name = "categories"),
    path("categories/<str:category>",views.categories2,name = "categories2"),
    path("listings/<int:listing_id>",views.listings,name="listings"),
    path("comment",views.comment,name = "comment"),
    path("bid",views.bid,name = "bid"),
    path("close",views.close,name="close"),
    path("open",views.open,name="open"),
    path("follow",views.follow,name="follow"),
    path("unfollow",views.unfollow,name="unfollow"),
]

