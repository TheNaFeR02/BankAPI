from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transactions import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'cards', views.CardViewSet)
router.register(r'accounts', views.AccountViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]