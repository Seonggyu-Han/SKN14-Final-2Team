"""
URL configuration for _01_django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include 
from django.shortcuts import render


def test_spinner_tip(request):
    """향수 지식 로더 테스트 페이지"""
    return render(request, 'test_spinner_tip.html')

def examples_page(request):
    """향수 지식 시스템 사용 예시 페이지"""
    return render(request, 'examples.html')

def demo_app(request):
    """향수 추천 앱 데모 페이지"""
    return render(request, 'demo-app.html')

def guide_page(request):
    """향수 지식 시스템 사용 가이드"""
    return render(request, 'guide.html')

def home_page(request):
    """메인 홈페이지"""
    return render(request, 'index.html')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("spinner-tip/", include("spinner_tip.urls", namespace="spinner_tip")),
    path("", home_page, name="home"),
    path("test/", test_spinner_tip, name="test_spinner_tip"),
    path("examples/", examples_page, name="examples"),
    path("demo/", demo_app, name="demo_app"),
    path("guide/", guide_page, name="guide"),
]
