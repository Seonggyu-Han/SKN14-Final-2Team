# uauth/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserDetail

@login_required
def complete_profile(request):
    detail = request.user.detail
    if request.method == "POST":
        detail.gender = request.POST.get("gender")
        detail.birth_year = request.POST.get("birth_year")
        detail.save()
        return redirect("/chat/")  # 저장 후 메인 페이지로 이동
    return render(request, "uauth/complete_profile.html", {"detail": detail})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "로그인되었습니다.")
                return redirect("/")  # 메인 페이지로 리디렉션
            else:
                return render(request, "uauth/login.html", {
                    "error": "아이디 또는 비밀번호가 올바르지 않습니다.",
                    "form_data": request.POST
                })
        else:
            return render(request, "uauth/login.html", {
                "error": "아이디와 비밀번호를 모두 입력하세요.",
                "form_data": request.POST
            })
    
    return render(request, "uauth/login.html")

def register(request):
    if request.method == "POST":
        # 폼 데이터 받기
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        name = request.POST.get("name")
        email = request.POST.get("email")
        birth_year = request.POST.get("birth_year")
        gender = request.POST.get("gender")
        
        # 유효성 검사
        errors = []
        
        if not username:
            errors.append("아이디를 입력하세요.")
        elif User.objects.filter(username=username).exists():
            errors.append("이미 존재하는 아이디입니다.")
            
        if not password1:
            errors.append("비밀번호를 입력하세요.")
        elif len(password1) < 8:
            errors.append("비밀번호는 8자 이상이어야 합니다.")
            
        if password1 != password2:
            errors.append("비밀번호가 일치하지 않습니다.")
            
        if not name:
            errors.append("이름을 입력하세요.")
            
        if not email:
            errors.append("이메일을 입력하세요.")
            
        if not birth_year:
            errors.append("출생연도를 입력하세요.")
        else:
            try:
                birth_year = int(birth_year)
                if birth_year < 1900 or birth_year > 2100:
                    errors.append("올바른 출생연도를 입력하세요.")
            except ValueError:
                errors.append("올바른 출생연도를 입력하세요.")
                
        if not gender:
            errors.append("성별을 선택하세요.")
            
        # 오류가 있으면 다시 폼 표시
        if errors:
            return render(request, "uauth/register.html", {
                "errors": errors,
                "form_data": request.POST
            })
        
        # 사용자 생성
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # UserDetail 생성
            UserDetail.objects.create(
                user=user,
                name=name,
                gender=gender,
                birth_year=birth_year
            )
            
            # 자동 로그인
            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                messages.success(request, "회원가입이 완료되었습니다.")
                return redirect("/chat/")  # chat 페이지로 리디렉션
            
        except Exception as e:
            messages.error(request, "회원가입 중 오류가 발생했습니다.")
            return render(request, "uauth/register.html", {
                "error": "회원가입 중 오류가 발생했습니다.",
                "form_data": request.POST
            })
    
    return render(request, "uauth/register.html")

def mypage(request):
    return render(request, "uauth/mypage.html")


