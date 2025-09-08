from django.urls import path
from .views import loading_fact_json, perfume_list, perfume_detail, perfume_search_api, perfume_recommendation_api

app_name = "spinner_tip"

urlpatterns = [
    path("fact/", loading_fact_json, name="fact"),
    path("perfumes/", perfume_list, name="perfume_list"),
    path("perfume/<int:pk>/", perfume_detail, name="perfume_detail"),
    path("api/perfume-search/", perfume_search_api, name="perfume_search_api"),
    path("api/perfume-recommendations/", perfume_recommendation_api, name="perfume_recommendation_api"),
]
