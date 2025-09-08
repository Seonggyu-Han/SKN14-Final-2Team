from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from uauth.models import UserDetail
from uauth.utils import process_profile_image, upload_to_s3_and_get_url

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

def product_detail(request, slug):
    # TODO: slug로 DB 조회 후 컨텍스트 바인딩
    ctx = {
        "brand": "Chanel",
        "name": "블루 드 샤넬",
        "price": "₩165,000",
        "slug": slug,
    }
    return render(request, "scentpick/product_detail.html", ctx)

def offlines(request):
    return render(request, "scentpick/offlines.html")

@login_required
def mypage(request):
    return render(request, "scentpick/mypage.html")

@login_required
def profile_edit(request):
    user: User = request.user
    detail: UserDetail = user.detail
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        gender = request.POST.get("gender")
        birth_year = request.POST.get("birth_year")
        file = request.FILES.get("profile_image")

        errors = []
        if not email:
            errors.append("이메일을 입력하세요.")
        # 간단 이메일 형식 체크는 생략 (Django form 사용시 강화 가능)

        # birth_year 검증
        if birth_year:
            try:
                by = int(birth_year)
                if by < 1900 or by > 2100:
                    errors.append("올바른 출생연도를 입력하세요.")
            except ValueError:
                errors.append("올바른 출생연도를 입력하세요.")

        if errors:
            return render(request, "scentpick/profile_edit.html", {
                "errors": errors,
                "form_data": request.POST,
                "detail": detail,
            })

        # 저장
        user.email = email
        user.save()
        if gender:
            detail.gender = gender
        if birth_year:
            detail.birth_year = int(birth_year)

        # 프로필 이미지 처리 (선택)
        if file:
            try:
                ctype = getattr(file, "content_type", "").lower()
                allowed_ct = {"image/jpeg", "image/png", "image/gif"}
                if ctype not in allowed_ct:
                    import imghdr
                    file.seek(0)
                    kind = (imghdr.what(file) or "").lower()
                    if kind == "jpg":
                        kind = "jpeg"
                    if kind not in {"jpeg", "png", "gif"}:
                        raise ValueError("지원 형식은 JPG/PNG/GIF 입니다.")

                crop = {
                    "x": request.POST.get("crop_x"),
                    "y": request.POST.get("crop_y"),
                    "size": request.POST.get("crop_size"),
                    "scale": request.POST.get("crop_scale"),
                }
                file.seek(0)
                image_bytes = process_profile_image(file, crop=crop)
                url = upload_to_s3_and_get_url(user.id, image_bytes, ext="jpg")
                detail.profile_image_url = url
            except Exception as e:
                messages.warning(request, f"프로필 이미지 처리 중 오류: {e}")

        detail.save()
        messages.success(request, "회원정보가 수정되었습니다.")
        return redirect("scentpick:mypage")

    # GET
    ctx = {
        "detail": detail,
    }
    return render(request, "scentpick/profile_edit.html", ctx)

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "비밀번호가 변경되었습니다.")
            return redirect('scentpick:mypage')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'scentpick/password_change.html', { 'form': form })

