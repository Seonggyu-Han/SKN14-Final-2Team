# scentpick/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

USER_MODEL = settings.AUTH_USER_MODEL  # 기본값: auth.User


class Perfume(models.Model):
    id = models.BigAutoField(primary_key=True)
    brand = models.CharField(max_length=50)                       # text
    name = models.CharField(max_length=50)                        # text
    eng_name = models.CharField(max_length=100)                        # text
    size_ml = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        help_text="(ml)",
    )
    price_krw = models.IntegerField(blank=True, null=True)         # int
    detail_url = models.TextField(blank=True, null=True)           # text
    description = models.TextField(blank=True, null=True)          # text
    concentration = models.CharField(max_length=30, blank=True, null=True)

    # 노트 / 어코드
    main_accords = models.TextField(blank=True, null=True)
    top_notes = models.TextField(blank=True, null=True)
    middle_notes = models.TextField(blank=True, null=True)
    base_notes = models.TextField(blank=True, null=True)

    # 점수 / 추천 지표
    notes_score = models.TextField(blank=True, null=True)
    season_score = models.TextField(blank=True, null=True)
    day_night_score = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)           # timestamp
    updated_at = models.DateTimeField(auto_now=True)               # timestamp

    class Meta:
        db_table = "perfumes"
        indexes = [
            models.Index(fields=["brand"]),
            models.Index(fields=["name"]),
            models.Index(fields=["eng_name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name", "eng_name", "size_ml"],
                name="uq_perfume_brand_name_eng_size_ml",
            ),
        ]

    def __str__(self):
        return f"{self.brand} {self.name} ({self.size_ml or ''}ml)".strip()


class Rating(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )  # FK는 auth_user로 연결 (UserDetail 아님)
    perfume = models.ForeignKey(
        Perfume, on_delete=models.CASCADE, related_name="ratings"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # int (1~5 권장)
    created_at = models.DateTimeField(auto_now_add=True)           # timestamp
    updated_at = models.DateTimeField(auto_now=True)               # timestamp

    class Meta:
        db_table = "ratings"
        constraints = [
            models.UniqueConstraint(fields=["user", "perfume"], name="uq_rating_user_perfume"),
        ]
        indexes = [
            models.Index(fields=["perfume"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user_id}→{self.perfume_id}:{self.score}"


class Favorite(models.Model):
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )  # FK는 auth_user로 연결
    perfume = models.ForeignKey(
        Perfume, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorites"
        constraints = [
            models.UniqueConstraint(fields=["user", "perfume"], name="uq_favorite_user_perfume"),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["perfume"]),
        ]

    def __str__(self):
        return f"{self.user_id} ♥ {self.perfume_id}"


class Conversation(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name="conversations"
    )  # FK는 auth_user로 연결
    title = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)            # timestamp
    updated_at = models.DateTimeField(auto_now=True)                # timestamp

    class Meta:
        db_table = "conversations"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self):
        return f"Conv#{self.pk}"


class Message(models.Model):
    class Role(models.TextChoices):
        SYSTEM = "system", "system"
        USER = "user", "user"
        ASSISTANT = "assistant", "assistant"

    id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=Role.choices)    # text
    content = models.TextField()                                    # text
    model = models.CharField(max_length=120, blank=True, null=True) # text
    created_at = models.DateTimeField(auto_now_add=True)            # timestamp

    class Meta:
        db_table = "messages"
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.role}@{self.conversation_id}"


class NoteImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    note_name = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "images"

    def __str__(self):
        return self.note_name or f"Image#{self.pk}"