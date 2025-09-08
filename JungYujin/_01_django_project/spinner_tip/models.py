from django.db import models
from django.urls import reverse
import json

class Perfume(models.Model):
    GENDER_CHOICES = [
        ('Male', '남성'),
        ('Female', '여성'),
        ('Unisex', '유니섹스'),
    ]
    
    CONCENTRATION_CHOICES = [
        ('오 드 퍼퓸', '오 드 퍼퓸 (EDP)'),
        ('오 드 뚜왈렛', '오 드 뚜왈렛 (EDT)'),
        ('오 드 코롱', '오 드 코롱 (EDC)'),
        ('퍼퓸', '퍼퓸 (Parfum)'),
    ]
    
    # 기본 정보
    brand = models.CharField(max_length=100, verbose_name='브랜드')
    name = models.CharField(max_length=200, verbose_name='향수명')
    detail_url = models.URLField(blank=True, null=True, verbose_name='상세 URL')
    concentration = models.CharField(max_length=50, choices=CONCENTRATION_CHOICES, verbose_name='농도')
    description = models.TextField(verbose_name='설명')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='성별')
    
    # 이미지 정보
    image = models.ImageField(upload_to='perfume_images/', blank=True, null=True, verbose_name='향수 이미지')
    image_url = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    
    # 향수 노트
    main_accords = models.CharField(max_length=500, verbose_name='메인 어코드')
    top_notes = models.CharField(max_length=500, verbose_name='톱 노트')
    middle_notes = models.CharField(max_length=500, verbose_name='미들 노트')
    base_notes = models.CharField(max_length=500, verbose_name='베이스 노트')
    
    # 점수 및 평가 (JSON 형태로 저장)
    notes_score = models.TextField(verbose_name='노트 점수', help_text='JSON 형태')
    season_score = models.TextField(verbose_name='계절 점수', help_text='JSON 형태')
    day_night_score = models.TextField(verbose_name='시간대 점수', help_text='JSON 형태')
    
    # 사이즈 정보
    sizes = models.CharField(max_length=200, verbose_name='사이즈')
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'perfumes'
        verbose_name = '향수'
        verbose_name_plural = '향수들'
        ordering = ['brand', 'name']
    
    def __str__(self):
        return f"{self.brand} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('perfume_detail', kwargs={'pk': self.pk})
    
    def get_notes_score_dict(self):
        """노트 점수를 딕셔너리로 반환"""
        try:
            # notes_score는 "rose(100.0) / oud(97.2) / woody(67.1)" 형태
            scores = {}
            if self.notes_score:
                for item in self.notes_score.split(' / '):
                    if '(' in item and ')' in item:
                        note = item.split('(')[0].strip()
                        score = float(item.split('(')[1].replace(')', ''))
                        scores[note] = score
            return scores
        except:
            return {}
    
    def get_season_score_dict(self):
        """계절 점수를 딕셔너리로 반환"""
        try:
            scores = {}
            if self.season_score:
                for item in self.season_score.split(' / '):
                    if '(' in item and ')' in item:
                        season = item.split('(')[0].strip()
                        score = float(item.split('(')[1].replace(')', ''))
                        scores[season] = score
            return scores
        except:
            return {}
    
    def get_day_night_score_dict(self):
        """시간대 점수를 딕셔너리로 반환"""
        try:
            scores = {}
            if self.day_night_score:
                for item in self.day_night_score.split(' / '):
                    if '(' in item and ')' in item:
                        time = item.split('(')[0].strip()
                        score = float(item.split('(')[1].replace(')', ''))
                        scores[time] = score
            return scores
        except:
            return {}
    
    def get_sizes_list(self):
        """사이즈를 리스트로 반환"""
        try:
            import ast
            return ast.literal_eval(self.sizes)
        except:
            return []
    
    def get_top_notes_list(self):
        """톱 노트를 리스트로 반환"""
        if not self.top_notes:
            return []
        return [note.strip() for note in self.top_notes.split() if note.strip()]
    
    def get_middle_notes_list(self):
        """미들 노트를 리스트로 반환"""
        if not self.middle_notes:
            return []
        return [note.strip() for note in self.middle_notes.split() if note.strip()]
    
    def get_base_notes_list(self):
        """베이스 노트를 리스트로 반환"""
        if not self.base_notes:
            return []
        return [note.strip() for note in self.base_notes.split() if note.strip()]
    
    def get_main_accords_list(self):
        """메인 어코드를 리스트로 반환"""
        if not self.main_accords:
            return []
        return [accord.strip() for accord in self.main_accords.split() if accord.strip()]
    
    def get_image_url(self):
        """향수 이미지 URL 반환 (업로드 이미지 우선, 없으면 외부 URL)"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            # 기본 이미지나 플레이스홀더 반환
            return None
    
    def get_placeholder_color(self):
        """브랜드명 기반 플레이스홀더 색상 생성"""
        colors = [
            ['#667eea', '#764ba2'],
            ['#f093fb', '#f5576c'], 
            ['#4facfe', '#00f2fe'],
            ['#43e97b', '#38f9d7'],
            ['#fa709a', '#fee140'],
            ['#a8edea', '#fed6e3'],
            ['#ff9a9e', '#fecfef'],
            ['#ffecd2', '#fcb69f']
        ]
        hash_value = sum(ord(char) for char in self.brand.lower())
        color_index = hash_value % len(colors)
        return colors[color_index]


class NoteImage(models.Model):
    """향수 노트 이미지 정보"""
    category = models.CharField(max_length=100, verbose_name='카테고리')
    note_name = models.CharField(max_length=200, verbose_name='노트명')
    image_url = models.URLField(verbose_name='이미지 URL')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'note_images'
        verbose_name = '노트 이미지'
        verbose_name_plural = '노트 이미지들'
        unique_together = ['note_name', 'image_url']  # 중복 방지
        ordering = ['category', 'note_name']
    
    def __str__(self):
        return f"{self.category} - {self.note_name}"
    
    @staticmethod
    def get_note_image_url(note_name):
        """노트명으로 이미지 URL 검색 (대소문자 무시)"""
        try:
            # 정확한 매칭 시도
            note_image = NoteImage.objects.filter(note_name__iexact=note_name).first()
            if note_image:
                return note_image.image_url
                
            # 부분 매칭 시도
            note_image = NoteImage.objects.filter(note_name__icontains=note_name).first()
            if note_image:
                return note_image.image_url
                
            return None
        except:
            return None
