# from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from scentpick import views as scentpick_views  # home 등



urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('app/', include('app.urls')),
    # path('', RedirectView.as_view(url='app/')),
    path(
        "accounts/login/redirect/",
        TemplateView.as_view(template_name="account/login_redirect.html"),
        name="account_login_redirect",
    ),
    path("accounts/", include("allauth.urls")),  # 소셜 로그인 경로
    path("uauth/", include("uauth.urls")),
    path("", scentpick_views.home, name="home"),
    path("", include("scentpick.urls")),
]
