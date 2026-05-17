from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EssayViewSet, EssayCategoryViewSet

#Intialize the specific router for the app
router = DefaultRouter()
router.register(r'essays', EssayViewSet, basename='essay')
router.register(r'categories', EssayCategoryViewSet, basename='category')

#Export the analyzer application URLs
urlpatterns = [
    path('', include(router.urls)),
]