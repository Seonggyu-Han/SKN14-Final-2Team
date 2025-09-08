# uauth/signals.py
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserDetail, OAuthAccount

@receiver(user_signed_up)
def create_user_detail_and_oauth(request, user, sociallogin=None, **kwargs):
    provider = sociallogin.account.provider          # google / naver / kakao
    extra_data = sociallogin.account.extra_data      # provider에서 받은 원시 데이터

    # OAuthAccount 저장
    provider_user_id = str(
        extra_data.get("id") or extra_data.get("sub")  # google=sub, naver/kakao=id
    )
    OAuthAccount.objects.get_or_create(
        user=user,
        provider=provider,
        provider_user_id=provider_user_id,
    )

    # UserDetail 생성
    detail, _ = UserDetail.objects.get_or_create(user=user)

    if provider == "naver":
        detail.gender = extra_data.get("gender")
        if "birthyear" in extra_data:
            detail.birth_year = int(extra_data["birthyear"])
        detail.name = extra_data.get("name") or user.username

    elif provider == "kakao":
        kakao_account = extra_data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        # 카카오 프로필 닉네임 사용
        detail.name = profile.get("nickname") or user.username

    elif provider == "google":
        # 구글은 name 필드 제공 (Full name)
        detail.name = extra_data.get("name") or user.username

    detail.save()
