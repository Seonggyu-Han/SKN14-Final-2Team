# views.py
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Perfume


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
    """perfumes 목록: MySQL Perfume에서 검색/필터/페이징"""
    q = (request.GET.get("q") or "").strip()
    brand_sel = request.GET.getlist("brand")
    size_sel = request.GET.getlist("size")
    gender_sel = request.GET.getlist("gender")
    conc_sel = request.GET.getlist("conc")

    qs = Perfume.objects.all()

    # 검색어
    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(brand__icontains=q)
            | Q(description__icontains=q)
            | Q(main_accords__icontains=q)
            | Q(top_notes__icontains=q)
            | Q(middle_notes__icontains=q)
            | Q(base_notes__icontains=q)
        )

    # 브랜드
    if brand_sel:
        qs = qs.filter(brand__in=brand_sel)

    # 용량
    if size_sel:
        size_q = Q()
        for s in size_sel:
            try:
                s_int = int(s)
                size_q |= Q(sizes__contains=s_int)
            except ValueError:
                pass
        if size_q:
            qs = qs.filter(size_q)

    # 성별
    if gender_sel:
        gq = Q()
        for g in gender_sel:
            gq |= Q(gender__iexact=g)
        if gq:
            qs = qs.filter(gq)

    # 농도
    if conc_sel:
        cq = Q()
        for c in conc_sel:
            cq |= Q(concentration__icontains=c)
        if cq:
            qs = qs.filter(cq)

    qs = qs.order_by("brand", "name")

    # 페이지네이션
    paginator = Paginator(qs, 24)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 페이지 range 커스텀
    current = page_obj.number
    total = paginator.num_pages
    page_range_custom = []

    if total <= 10:
        page_range_custom = list(range(1, total + 1))
    else:
        if current <= 6:
            page_range_custom = list(range(1, 7)) + ["...", total]
        elif current >= total - 5:
            page_range_custom = [1, "..."] + list(range(total - 5, total + 1))
        else:
            page_range_custom = [1, "..."] + list(range(current - 2, current + 3)) + ["...", total]

    # 카드 데이터 가공
    for p in page_obj.object_list:
        raw = (p.main_accords or "")
        if "," in raw:
            toks = [t.strip() for t in raw.split(",")]
        else:
            toks = [t.strip() for t in raw.split()]
        p.accord_list = [t for t in toks if t][:6]
        p.image_url = f"https://scentpick-images.s3.ap-northeast-2.amazonaws.com/perfumes/{p.id}.jpg"

    # 필터 옵션
    brands = Perfume.objects.values_list("brand", flat=True).distinct().order_by("brand")
    concentrations = (
        Perfume.objects.exclude(concentration="")
        .values_list("concentration", flat=True)
        .distinct()
        .order_by("concentration")
    )
    genders = (
        Perfume.objects.exclude(gender="")
        .values_list("gender", flat=True)
        .distinct()
        .order_by("gender")
    )

    base_qd = request.GET.copy()
    base_qd.pop("page", True)
    base_qs = base_qd.urlencode()

    ctx = {
        "page_obj": page_obj,
        "page_range_custom": page_range_custom,
        "brands": brands,
        "concentrations": concentrations,
        "genders": genders,
        "selected": {
            "q": q,
            "brand": brand_sel,
            "gender": gender_sel,
            "conc": conc_sel,
        },
        "base_qs": base_qs,
    }

    if request.GET.get("ajax") == "1":
        return render(request, "scentpick/perfumes_grid.html", ctx)

    return render(request, "scentpick/perfumes.html", ctx)


def product_detail(request, slug):
    ctx = {
        "brand": "Chanel",
        "name": "블루 드 샤넬",
        "price": "₩165,000",
        "slug": slug,
    }
    return render(request, "scentpick/product_detail.html", ctx)


def offlines(request):
    return render(request, "scentpick/offlines.html", {"KAKAO_JS_KEY": settings.KAKAO_JS_KEY})


def mypage(request):
    return render(request, "scentpick/mypage.html")
