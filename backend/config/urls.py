
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # Django Admin site
    path("admin/", admin.site.urls),

    # Accounts API endpoints
    path(
        "api/v1/auth/",
        include("accounts.urls")
    ),

    path(
        "api/v1/", 
        include("tickets.urls")
    ),
]

