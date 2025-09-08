from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.urls import reverse
from urllib.parse import urlencode

def _redir_with_next(next_url: str | None = None) -> str:
    base = reverse("account_login_redirect")  # /accounts/login/redirect/
    if next_url:    
        return f"{base}?{urlencode({'next': next_url})}"
    return base

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        provider = request.session.get("socialaccount_provider")

        needs_completion = (
            not hasattr(user, "detail")
            or not user.detail.gender
            or not user.detail.birth_year
        )

        if provider in ["google", "kakao"] and needs_completion:
            target = reverse("uauth:complete_profile")
        else:
            target = "/chat/"  # home 대신 chat으로 변경

        redirector = reverse("account_login_redirect")
        return f"{redirector}?next={target}"
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """소셜 로그인 후 사용자 정보를 커스터마이징"""

    def pre_social_login(self, request, sociallogin):
        # 어떤 provider로 로그인했는지 세션에 저장
        request.session["socialaccount_provider"] = sociallogin.account.provider

    def get_login_redirect_url(self, request):
        user = request.user
        provider = request.session.get("socialaccount_provider")

        # 목적지 계산
        needs_completion = (
            not hasattr(user, "detail")
            or not user.detail.gender
            or not user.detail.birth_year
        )

        if provider in ["google", "kakao"] and needs_completion:
            target = reverse("uauth:complete_profile")
        else:
            target = reverse("home")

        # ✅ 반드시 중간 페이지로 보내서 팝업 닫기
        redirector = reverse("account_login_redirect")
        return f"{redirector}?next={target}"
    
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        extra_data = sociallogin.account.extra_data

        if not user.email:
            user.email = extra_data.get("email", "")
            user.save()
        return user

    # def get_signup_redirect_url(self, request):
    #     # 소셜 회원가입 후 이동할 페이지
    #     return reverse("uauth:complete_profile")
