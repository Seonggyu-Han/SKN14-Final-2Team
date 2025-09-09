from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserDetail(models.Model):
    """
    users
    Django 기본 User와 1:1 매핑하여 'users' 테이블로 확장
    - PK = auth_user.id (FK 겸용)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="id",
        related_name="detail",  # user.detail 로 접근
    )

    name = models.CharField(max_length=60, blank=True, null=True)          # text
    gender = models.CharField(max_length=10, blank=True, null=True)        # text
    birth_year = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )  # int

    # 프로필 이미지의 절대 URL (S3 등 외부 스토리지 주소)
    profile_image_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)                   # timestamp
    updated_at = models.DateTimeField(auto_now=True)                       # timestamp

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["gender"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "User Detail"
        verbose_name_plural = "User Details"

    def __str__(self):
        # 이메일은 auth_user 테이블에 있으므로 user.email 사용
        base = self.name or (self.user.email or self.user.username)
        return f"{base} (#{self.pk})"

    @property
    def avatar_url(self) -> str:
        """프로필 이미지 URL이 없으면 기본 이미지를 반환"""
        base = "https://scentpick-images.s3.ap-northeast-2.amazonaws.com/profiles/default.jpg"
        if self.profile_image_url:
            # Cache-busting using updated_at timestamp
            try:
                ts = int(self.updated_at.timestamp()) if self.updated_at else 0
            except Exception:
                ts = 0
            sep = '&' if '?' in self.profile_image_url else '?'
            return f"{self.profile_image_url}{sep}v={ts}"
        return base


class OAuthAccount(models.Model):
    """
    oauth_accounts (User : OAuthAccount = 1 : N)
    - 같은 provider 내 동일 계정 중복 연결 방지
    - 한 사용자가 동일 provider를 중복 연결하지 않도록 UK 추가
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="oauth_accounts")
    provider = models.CharField(max_length=40)                 # e.g., google / naver / kakao
    provider_user_id = models.CharField(max_length=120)        # 공급자 시스템 내 사용자 ID

    class Meta:
        db_table = "oauth_accounts"
        constraints = [
            # 같은 provider에서 동일 계정 중복 연결 방지
            models.UniqueConstraint(
                fields=["provider", "provider_user_id"],
                name="uq_oauth_provider_user",
            ),
            # 한 사용자가 동일 provider를 중복 연결하지 못하도록
            models.UniqueConstraint(
                fields=["user", "provider"],
                name="uq_oauth_user_provider",
            ),
        ]
        indexes = [
            models.Index(fields=["provider"]),
            models.Index(fields=["provider_user_id"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_user_id}"
