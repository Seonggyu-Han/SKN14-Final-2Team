#!/usr/bin/env python
"""
기존 향수 데이터에 이미지 URL을 추가하는 스크립트
"""
import os
import sys
import django
import pandas as pd

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_01_django_project.settings')
django.setup()

from spinner_tip.models import Perfume

def update_perfume_images():
    """기존 향수 데이터에 이미지 URL 추가"""
    
    # 이미지 URL이 포함된 CSV 파일 읽기
    try:
        image_df = pd.read_csv('output_with_images_clean.csv')
        print(f"이미지 CSV 파일에서 {len(image_df)}개의 데이터를 읽었습니다.")
    except FileNotFoundError:
        print("ERROR: output_with_images_clean.csv 파일을 찾을 수 없습니다.")
        return
    
    # 기존 향수 데이터 가져오기
    existing_perfumes = Perfume.objects.all()
    print(f"데이터베이스에서 {existing_perfumes.count()}개의 기존 향수 데이터를 찾았습니다.")
    
    updated_count = 0
    not_found_count = 0
    
    # 각 향수에 대해 이미지 URL 찾기 및 업데이트
    for perfume in existing_perfumes:
        # 브랜드와 향수명으로 이미지 찾기
        matching_images = image_df[
            (image_df['brand'] == perfume.brand) & 
            (image_df['name'] == perfume.name)
        ]
        
        if not matching_images.empty:
            # 첫 번째 매칭되는 이미지 URL 사용
            image_url = matching_images.iloc[0]['image_url']
            
            # NaN이 아니고 실제 URL인 경우에만 업데이트
            if pd.notna(image_url) and isinstance(image_url, str) and image_url.startswith('http'):
                perfume.image_url = image_url
                perfume.save()
                updated_count += 1
                print(f"✓ {perfume.brand} - {perfume.name}: 이미지 URL 업데이트됨")
            else:
                not_found_count += 1
                print(f"✗ {perfume.brand} - {perfume.name}: 유효한 이미지 URL이 없음")
        else:
            not_found_count += 1
            print(f"✗ {perfume.brand} - {perfume.name}: 매칭되는 이미지를 찾을 수 없음")
    
    print(f"\n=== 업데이트 완료 ===")
    print(f"이미지 URL 업데이트됨: {updated_count}개")
    print(f"이미지를 찾을 수 없음: {not_found_count}개")
    print(f"전체: {updated_count + not_found_count}개")

def show_sample_images():
    """이미지가 있는 향수들 샘플 보기"""
    perfumes_with_images = Perfume.objects.filter(image_url__isnull=False).exclude(image_url='')[:5]
    
    print(f"\n=== 이미지가 있는 향수 샘플 ({perfumes_with_images.count()}개) ===")
    for perfume in perfumes_with_images:
        print(f"브랜드: {perfume.brand}")
        print(f"이름: {perfume.name}")
        print(f"이미지 URL: {perfume.image_url}")
        print("-" * 50)

if __name__ == "__main__":
    print("향수 이미지 URL 업데이트 시작")
    print("=" * 50)
    
    update_perfume_images()
    show_sample_images()
