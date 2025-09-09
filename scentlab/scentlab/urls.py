from django.urls import path, include
from django.views.generic import TemplateView
from scentpick import views as scentpick_views

urlpatterns = [
    path('accounts/login/redirect/', TemplateView.as_view(template_name='account/login_redirect.html'), name='account_login_redirect'),
    path('accounts/', include('allauth.urls')),
    path('uauth/', include('uauth.urls')),
    path('', scentpick_views.home, name='home'),
    path('', include('scentpick.urls')),
]

