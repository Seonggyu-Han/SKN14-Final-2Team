from django.contrib import admin
from django.urls import path
from . import views

app_name = 'scentpick'

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.chat, name="chat"),
    path("recommend/", views.recommend, name="recommend"),
    path("perfumes/", views.perfumes, name="perfumes"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),  # ✅ id(pk)로 수정
    path("offlines/", views.offlines, name="offlines"),
    path("mypage/", views.mypage, name="mypage"),
]
