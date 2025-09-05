from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.db.models import Q
from .services.fact_service import FactService
from .models import Perfume
import logging
import random

logger = logging.getLogger(__name__)
fact_service = FactService()

@require_GET
@cache_page(60 * 5)  # 5분간 캐시
def loading_fact_json(request):
    """
    스피너 대신 보여줄 랜덤 향수 지식 한 줄
    - random.choice로 향수 지식 리스트에서 랜덤 선택
    - 캐시를 통해 성능 최적화
    """
    try:
        # 매번 새로운 랜덤 선택을 위해 캐시를 초기화하지 않고 직접 선택
        facts = fact_service.repo.load()
        fact = random.choice(facts)
        logger.info(f"Random perfume fact served: {fact[:50]}...")
        return JsonResponse({
            "fact": fact,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error getting random fact: {e}")
        # 폴백 메시지
        fallback_fact = "향수의 첫인상은 톱 노트, 그 다음이 미들 노트, 마지막이 베이스 노트입니다."
        return JsonResponse({
            "fact": fallback_fact,
            "status": "fallback"
        })

def perfume_list(request):
    """향수 전체 리스트 페이지"""
    perfumes = Perfume.objects.all()
    
    # 검색 기능
    search_query = request.GET.get('search', '')
    if search_query:
        perfumes = perfumes.filter(
            Q(name__icontains=search_query) | 
            Q(brand__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 필터링
    brand = request.GET.get('brand', '')
    gender = request.GET.get('gender', '')
    concentration = request.GET.get('concentration', '')
    
    if brand:
        perfumes = perfumes.filter(brand=brand)
    if gender:
        perfumes = perfumes.filter(gender=gender)
    if concentration:
        perfumes = perfumes.filter(concentration=concentration)
    
    # 페이지네이션
    paginator = Paginator(perfumes, 20)  # 페이지당 20개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 필터 옵션을 위한 데이터
    brands = Perfume.objects.values_list('brand', flat=True).distinct().order_by('brand')
    genders = Perfume.GENDER_CHOICES
    concentrations = Perfume.CONCENTRATION_CHOICES
    
    context = {
        'page_obj': page_obj,
        'perfumes': page_obj,
        'search_query': search_query,
        'brands': brands,
        'genders': genders,
        'concentrations': concentrations,
        'selected_brand': brand,
        'selected_gender': gender,
        'selected_concentration': concentration,
        'total_count': perfumes.count(),
    }
    
    return render(request, 'spinner_tip/perfume_list.html', context)

def perfume_detail(request, pk):
    """향수 상세 페이지"""
    perfume = get_object_or_404(Perfume, pk=pk)
    
    # 노트별 이미지 매핑 함수
    def get_note_image_url(note_name):
        # SQL 파일에서 가져온 실제 노트 이미지 매핑 (훨씬 더 많은 노트들)
        note_images = {
            # Citrus 계열
            'bergamot': 'https://fimgs.net/mdimg/sastojci/m.75.jpg',
            'bigarade': 'https://fimgs.net/mdimg/sastojci/m.1083.jpg',
            'bitter orange': 'https://fimgs.net/mdimg/sastojci/m.79.jpg',
            'blood orange': 'https://fimgs.net/mdimg/sastojci/m.286.jpg',
            'grapefruit': 'https://fimgs.net/mdimg/sastojci/m.76.jpg',
            'lemon': 'https://fimgs.net/mdimg/sastojci/m.77.jpg',
            'lime': 'https://fimgs.net/mdimg/sastojci/m.78.jpg',
            'mandarin orange': 'https://fimgs.net/mdimg/sastojci/m.82.jpg',
            'orange': 'https://fimgs.net/mdimg/sastojci/m.80.jpg',
            'yuzu': 'https://fimgs.net/mdimg/sastojci/m.83.jpg',
            
            # Floral 계열
            'rose': 'https://fimgs.net/mdimg/sastojci/m.15.jpg',
            'jasmine': 'https://fimgs.net/mdimg/sastojci/m.18.jpg',
            'neroli': 'https://fimgs.net/mdimg/sastojci/m.17.jpg',
            'lavender': 'https://fimgs.net/mdimg/sastojci/m.19.jpg',
            'lily': 'https://fimgs.net/mdimg/sastojci/m.20.jpg',
            'lily of the valley': 'https://fimgs.net/mdimg/sastojci/m.21.jpg',
            'peony': 'https://fimgs.net/mdimg/sastojci/m.22.jpg',
            'magnolia': 'https://fimgs.net/mdimg/sastojci/m.23.jpg',
            'iris': 'https://fimgs.net/mdimg/sastojci/m.24.jpg',
            'freesia': 'https://fimgs.net/mdimg/sastojci/m.25.jpg',
            'tuberose': 'https://fimgs.net/mdimg/sastojci/m.26.jpg',
            'ylang ylang': 'https://fimgs.net/mdimg/sastojci/m.27.jpg',
            'orange blossom': 'https://fimgs.net/mdimg/sastojci/m.28.jpg',
            
            # Woody 계열
            'sandalwood': 'https://fimgs.net/mdimg/sastojci/m.86.jpg',
            'cedar': 'https://fimgs.net/mdimg/sastojci/m.85.jpg',
            'cedarwood': 'https://fimgs.net/mdimg/sastojci/m.85.jpg',
            'oak moss': 'https://fimgs.net/mdimg/sastojci/m.84.jpg',
            'oakmoss': 'https://fimgs.net/mdimg/sastojci/m.84.jpg',
            'patchouli': 'https://fimgs.net/mdimg/sastojci/m.83.jpg',
            'vetiver': 'https://fimgs.net/mdimg/sastojci/m.87.jpg',
            'birch': 'https://fimgs.net/mdimg/sastojci/m.88.jpg',
            'birchwood': 'https://fimgs.net/mdimg/sastojci/m.88.jpg',
            'pine': 'https://fimgs.net/mdimg/sastojci/m.89.jpg',
            'juniper': 'https://fimgs.net/mdimg/sastojci/m.90.jpg',
            
            # Spicy 계열
            'pepper': 'https://fimgs.net/mdimg/sastojci/m.91.jpg',
            'pink pepper': 'https://fimgs.net/mdimg/sastojci/m.92.jpg',
            'black pepper': 'https://fimgs.net/mdimg/sastojci/m.93.jpg',
            'cinnamon': 'https://fimgs.net/mdimg/sastojci/m.94.jpg',
            'cardamom': 'https://fimgs.net/mdimg/sastojci/m.95.jpg',
            'ginger': 'https://fimgs.net/mdimg/sastojci/m.96.jpg',
            'nutmeg': 'https://fimgs.net/mdimg/sastojci/m.97.jpg',
            'clove': 'https://fimgs.net/mdimg/sastojci/m.98.jpg',
            'cloves': 'https://fimgs.net/mdimg/sastojci/m.98.jpg',
            
            # Oriental/Resinous 계열
            'vanilla': 'https://fimgs.net/mdimg/sastojci/m.99.jpg',
            'amber': 'https://fimgs.net/mdimg/sastojci/m.100.jpg',
            'musk': 'https://fimgs.net/mdimg/sastojci/m.101.jpg',
            'white musk': 'https://fimgs.net/mdimg/sastojci/m.102.jpg',
            'oud': 'https://fimgs.net/mdimg/sastojci/m.103.jpg',
            'agarwood': 'https://fimgs.net/mdimg/sastojci/m.103.jpg',
            'frankincense': 'https://fimgs.net/mdimg/sastojci/m.104.jpg',
            'myrrh': 'https://fimgs.net/mdimg/sastojci/m.105.jpg',
            'benzoin': 'https://fimgs.net/mdimg/sastojci/m.106.jpg',
            'labdanum': 'https://fimgs.net/mdimg/sastojci/m.107.jpg',
            
            # Fruity 계열
            'apple': 'https://fimgs.net/mdimg/sastojci/m.108.jpg',
            'green apple': 'https://fimgs.net/mdimg/sastojci/m.109.jpg',
            'pear': 'https://fimgs.net/mdimg/sastojci/m.110.jpg',
            'peach': 'https://fimgs.net/mdimg/sastojci/m.111.jpg',
            'apricot': 'https://fimgs.net/mdimg/sastojci/m.112.jpg',
            'blackberry': 'https://fimgs.net/mdimg/sastojci/m.113.jpg',
            'raspberry': 'https://fimgs.net/mdimg/sastojci/m.114.jpg',
            'strawberry': 'https://fimgs.net/mdimg/sastojci/m.115.jpg',
            'currant': 'https://fimgs.net/mdimg/sastojci/m.116.jpg',
            'black currant': 'https://fimgs.net/mdimg/sastojci/m.117.jpg',
            'pineapple': 'https://fimgs.net/mdimg/sastojci/m.118.jpg',
            'coconut': 'https://fimgs.net/mdimg/sastojci/m.119.jpg',
            'mango': 'https://fimgs.net/mdimg/sastojci/m.120.jpg',
            
            # Herbal/Green 계열
            'basil': 'https://fimgs.net/mdimg/sastojci/m.121.jpg',
            'mint': 'https://fimgs.net/mdimg/sastojci/m.122.jpg',
            'spearmint': 'https://fimgs.net/mdimg/sastojci/m.123.jpg',
            'rosemary': 'https://fimgs.net/mdimg/sastojci/m.124.jpg',
            'thyme': 'https://fimgs.net/mdimg/sastojci/m.125.jpg',
            'sage': 'https://fimgs.net/mdimg/sastojci/m.126.jpg',
            'green tea': 'https://fimgs.net/mdimg/sastojci/m.127.jpg',
            'tea': 'https://fimgs.net/mdimg/sastojci/m.127.jpg',
            
            # 한국어 노트들
            '베르가못': 'https://fimgs.net/mdimg/sastojci/m.75.jpg',
            '레몬': 'https://fimgs.net/mdimg/sastojci/m.77.jpg',
            '오렌지': 'https://fimgs.net/mdimg/sastojci/m.80.jpg',
            '자몽': 'https://fimgs.net/mdimg/sastojci/m.76.jpg',
            '장미': 'https://fimgs.net/mdimg/sastojci/m.15.jpg',
            '자스민': 'https://fimgs.net/mdimg/sastojci/m.18.jpg',
            '라벤더': 'https://fimgs.net/mdimg/sastojci/m.19.jpg',
            '샌달우드': 'https://fimgs.net/mdimg/sastojci/m.86.jpg',
            '시더우드': 'https://fimgs.net/mdimg/sastojci/m.85.jpg',
            '패출리': 'https://fimgs.net/mdimg/sastojci/m.83.jpg',
            '베티버': 'https://fimgs.net/mdimg/sastojci/m.87.jpg',
            '바닐라': 'https://fimgs.net/mdimg/sastojci/m.99.jpg',
            '머스크': 'https://fimgs.net/mdimg/sastojci/m.101.jpg',
            '앰버': 'https://fimgs.net/mdimg/sastojci/m.100.jpg',
            '애플': 'https://fimgs.net/mdimg/sastojci/m.108.jpg',
            '복숭아': 'https://fimgs.net/mdimg/sastojci/m.111.jpg',
            '파인애플': 'https://fimgs.net/mdimg/sastojci/m.118.jpg',
        }
        
        # 정확한 매칭 시도 (대소문자 무시)
        note_lower = note_name.lower().strip()
        for key, url in note_images.items():
            if note_lower == key.lower():
                return url
            
        # 부분 매칭 시도 (더 엄격하게)
        for key, url in note_images.items():
            # 키워드가 완전히 포함되어 있는 경우만
            if len(key) > 3 and key.lower() in note_lower:
                return url
            elif len(note_lower) > 3 and note_lower in key.lower():
                return url
                
        # 카테고리별 기본 이미지 (더 구체적으로)
        if any(word in note_lower for word in ['citrus', '시트러스', 'bergamot', 'grapefruit']):
            return 'https://fimgs.net/mdimg/sastojci/m.75.jpg'  # 베르가못
        elif any(word in note_lower for word in ['floral', '플로랄', 'flower', '꽃']):
            return 'https://fimgs.net/mdimg/sastojci/m.15.jpg'  # 장미
        elif any(word in note_lower for word in ['woody', '우디', 'wood', '나무']):
            return 'https://fimgs.net/mdimg/sastojci/m.86.jpg'  # 샌달우드
        elif any(word in note_lower for word in ['spicy', '스파이시', 'pepper']):
            return 'https://fimgs.net/mdimg/sastojci/m.91.jpg'  # 후추
        elif any(word in note_lower for word in ['oriental', '오리엔탈', 'amber', 'musk']):
            return 'https://fimgs.net/mdimg/sastojci/m.100.jpg'  # 앰버
        elif any(word in note_lower for word in ['fruit', '과일', 'apple', 'berry']):
            return 'https://fimgs.net/mdimg/sastojci/m.108.jpg'  # 애플
        else:
            # 완전히 모르는 노트는 카테고리별로 다른 이미지
            import hashlib
            hash_value = int(hashlib.md5(note_name.encode()).hexdigest()[:4], 16)
            default_images = [
                'https://fimgs.net/mdimg/sastojci/m.75.jpg',  # 베르가못
                'https://fimgs.net/mdimg/sastojci/m.15.jpg',  # 장미
                'https://fimgs.net/mdimg/sastojci/m.86.jpg',  # 샌달우드
                'https://fimgs.net/mdimg/sastojci/m.91.jpg',  # 후추
                'https://fimgs.net/mdimg/sastojci/m.100.jpg', # 앰버
            ]
            return default_images[hash_value % len(default_images)]
    
    # 노트별 이미지 URL 추가
    top_notes_with_images = []
    for note in perfume.get_top_notes_list():
        top_notes_with_images.append({
            'name': note,
            'image_url': get_note_image_url(note)
        })
    
    middle_notes_with_images = []
    for note in perfume.get_middle_notes_list():
        middle_notes_with_images.append({
            'name': note,
            'image_url': get_note_image_url(note)
        })
    
    base_notes_with_images = []
    for note in perfume.get_base_notes_list():
        base_notes_with_images.append({
            'name': note,
            'image_url': get_note_image_url(note)
        })

    context = {
        'perfume': perfume,
        'notes_score': perfume.get_notes_score_dict(),
        'season_score': perfume.get_season_score_dict(),
        'day_night_score': perfume.get_day_night_score_dict(),
        'sizes': perfume.get_sizes_list(),
        'top_notes': top_notes_with_images,
        'middle_notes': middle_notes_with_images,
        'base_notes': base_notes_with_images,
        'main_accords': perfume.get_main_accords_list(),
    }
    
    return render(request, 'spinner_tip/perfume_detail.html', context)

def perfume_search_api(request):
    """향수 검색 API (자동완성용)"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    perfumes = Perfume.objects.filter(
        Q(name__icontains=query) | Q(brand__icontains=query)
    )[:10]
    
    results = []
    for perfume in perfumes:
        results.append({
            'id': perfume.pk,
            'text': f"{perfume.brand} - {perfume.name}",
            'brand': perfume.brand,
            'name': perfume.name,
            'url': perfume.get_absolute_url()
        })
    
    return JsonResponse({'results': results})

def perfume_recommendation_api(request):
    """향수 추천 API (데모 앱용)"""
    gender = request.GET.get('gender', '')
    season = request.GET.get('season', '')
    
    # 기본 필터링
    perfumes = Perfume.objects.all()
    
    if gender:
        if gender == 'male':
            perfumes = perfumes.filter(gender='Male')
        elif gender == 'female':
            perfumes = perfumes.filter(gender='Female')
        elif gender == 'unisex':
            perfumes = perfumes.filter(gender='Unisex')
    
    # 계절별 필터링 (간단한 구현)
    if season:
        season_map = {
            'spring': 'spring',
            'summer': 'summer', 
            'autumn': 'fall',
            'winter': 'winter'
        }
        season_key = season_map.get(season, season)
        perfumes = perfumes.filter(season_score__icontains=f'{season_key}(')
    
    # 상위 6개 추천
    recommendations = perfumes[:6]
    
    results = []
    for perfume in recommendations:
        # 추천 이유 생성
        reason_parts = []
        if perfume.gender and gender:
            reason_parts.append(f"{perfume.get_gender_display()}용 향수")
        if season:
            reason_parts.append(f"{season} 계절에 적합")
        if perfume.main_accords:
            main_accord = perfume.main_accords.split()[0] if perfume.main_accords else ''
            if main_accord:
                reason_parts.append(f"{main_accord} 계열")
        
        reason = ', '.join(reason_parts) if reason_parts else "추천 향수"
        
        results.append({
            'id': perfume.pk,
            'name': perfume.name,
            'brand': perfume.brand,
            'reason': reason,
            'url': perfume.get_absolute_url(),
            'concentration': perfume.concentration,
            'description': perfume.description[:100] + '...' if len(perfume.description) > 100 else perfume.description
        })
    
    return JsonResponse({'recommendations': results})
