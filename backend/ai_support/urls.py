from django.urls import path
from .views import ULTRONChatAPIView

urlpatterns = [
    path("chat/", 
        ULTRONChatAPIView.as_view(), 
        name="ultron-chat"
    ),
    
]