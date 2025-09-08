from django.contrib import admin
from django.urls import path
from . import views

app_name = 'scentpick'

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.chat, name="chat"),
    path("recommend/", views.recommend, name="recommend"),
    path("perfumes/", views.perfumes, name="perfumes"),
    path("all-perfumes/", views.all_perfumes, name="all_perfumes"),  # 새로 추가
    path("perfume/<int:perfume_id>/", views.product_detail, name="product_detail"), 
    path('api/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path("offlines/", views.offlines, name="offlines"),
    path("mypage/", views.mypage, name="mypage"),
]

# slug 를 perfume_id 로 수정함