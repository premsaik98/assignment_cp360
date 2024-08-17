from django.urls import path
from .views import register, activate, CustomLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
