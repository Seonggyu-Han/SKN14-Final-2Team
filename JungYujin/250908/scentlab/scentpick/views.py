from django.shortcuts import render, get_object_or_404 
from .models import Perfume, Favorite
# from .models import Note
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

def home(request):
    return render(request, "scentpick/home.html")

def login_view(request):
    return render(request, "scentpick/login.html")

def register(request):
    return render(request, "scentpick/register.html")

def chat(request):
    return render(request, "scentpick/chat.html")

def recommend(request):
    return render(request, "scentpick/recommend.html")

def perfumes(request):
    return render(request, "scentpick/perfumes.html")

# product_detail 함수 수정

def product_detail(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)
    image_url = f"https://scentpick-images.s3.ap-northeast-2.amazonaws.com/perfumes/{perfume.id}.jpg"
    
    def safe_process_json_field(field_data):
        if not field_data:
            return []
        
        try:
            # Case 1: 이미 Python 리스트인 경우
            if isinstance(field_data, list):
                return field_data
            
            # Case 2: JSON 문자열인 경우 (예: '["레몬", "자몽"]')
            if isinstance(field_data, str):
                import json
                try:
                    parsed = json.loads(field_data)
                    if isinstance(parsed, list):
                        return parsed
                except:
                    # Case 3: JSON 파싱 실패시 공백으로 분리 (예: '레몬 자몽')
                    return field_data.split()
            
            return []
        except Exception as e:
            print(f"Error processing field: {field_data}, Error: {e}")
            return []
    
    main_accords = safe_process_json_field(perfume.main_accords)
    top_notes = safe_process_json_field(perfume.top_notes)
    middle_notes = safe_process_json_field(perfume.middle_notes)
    base_notes = safe_process_json_field(perfume.base_notes)
    
    # 이전/다음 향수 가져오기
    prev_perfume = Perfume.objects.filter(id__lt=perfume_id).order_by('-id').first()
    next_perfume = Perfume.objects.filter(id__gt=perfume_id).order_by('id').first()

    context = {
        'perfume': perfume,
        'image_url': image_url,
        'main_accords': main_accords,
        'top_notes': top_notes,
        'middle_notes': middle_notes,
        'base_notes': base_notes,
        'sizes': perfume.sizes,
        'gender': perfume.gender,
        'prev_perfume': prev_perfume,
        'next_perfume': next_perfume,
    }
    return render(request, 'scentpick/product_detail.html', context)

@require_POST
@login_required
def toggle_favorite(request):
    try:
        data = json.loads(request.body)
        perfume_id = data.get('perfume_id')
        perfume = get_object_or_404(Perfume, id=perfume_id)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            perfume=perfume
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def offlines(request):
    return render(request, "scentpick/offlines.html")

@login_required
def mypage(request):
    # 사용자의 즐겨찾기 향수 가져오기
    favorite_perfumes = Perfume.objects.filter(
        favorite__user=request.user
    ).order_by('-favorite__created_at')
    
    context = {
        'favorite_perfumes': favorite_perfumes
    }
    return render(request, "scentpick/mypage.html", context)

def all_perfumes(request):
    """전체 향수 목록 페이지 (1번~802번)"""
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    # 페이지당 20개씩 표시
    per_page = 20
    offset = (page - 1) * per_page
    
    perfumes = Perfume.objects.all().order_by('id')[offset:offset + per_page]
    total_count = Perfume.objects.count()
    total_pages = (total_count + per_page - 1) // per_page
    
    # 페이지네이션 정보
    has_previous = page > 1
    has_next = page < total_pages
    previous_page = page - 1 if has_previous else None
    next_page = page + 1 if has_next else None
    
    context = {
        'perfumes': perfumes,
        'current_page': page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_page': previous_page,
        'next_page': next_page,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
    }
    return render(request, 'scentpick/all_perfumes.html', context)

