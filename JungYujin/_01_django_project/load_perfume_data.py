#!/usr/bin/env python
"""
CSV 파일에서 향수 데이터를 읽어와 Django 데이터베이스에 저장하는 스크립트
"""
import os
import sys
import django
import csv
import pandas as pd

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_01_django_project.settings')
django.setup()

from spinner_tip.models import Perfume

def load_perfume_data():
    """CSV 파일에서 향수 데이터를 로드"""
    csv_file_path = '../perfume_final.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"CSV 파일을 찾을 수 없습니다: {csv_file_path}")
        return
    
    # 기존 데이터 삭제 여부 확인
    existing_count = Perfume.objects.count()
    if existing_count > 0:
        response = input(f"기존 향수 데이터 {existing_count}개가 있습니다. 삭제하고 새로 로드하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            Perfume.objects.all().delete()
            print(f"기존 데이터 {existing_count}개를 삭제했습니다.")
        else:
            print("데이터 로드를 취소했습니다.")
            return
    
    success_count = 0
    error_count = 0
    
    try:
        # pandas로 CSV 읽기 (한글 인코딩 처리)
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        print(f"CSV 파일에서 {len(df)}개의 향수 데이터를 읽었습니다.")
        print("데이터베이스에 저장 중...")
        
        for index, row in df.iterrows():
            try:
                # Perfume 객체 생성
                perfume = Perfume(
                    brand=str(row['brand']) if pd.notna(row['brand']) else '',
                    name=str(row['name']) if pd.notna(row['name']) else '',
                    detail_url=str(row['detail_url']) if pd.notna(row['detail_url']) else '',
                    concentration=str(row['concentration']) if pd.notna(row['concentration']) else '',
                    main_accords=str(row['main_accords']) if pd.notna(row['main_accords']) else '',
                    top_notes=str(row['top_notes']) if pd.notna(row['top_notes']) else '',
                    middle_notes=str(row['middle_notes']) if pd.notna(row['middle_notes']) else '',
                    base_notes=str(row['base_notes']) if pd.notna(row['base_notes']) else '',
                    description=str(row['description']) if pd.notna(row['description']) else '',
                    notes_score=str(row['notes_score']) if pd.notna(row['notes_score']) else '',
                    season_score=str(row['season_score']) if pd.notna(row['season_score']) else '',
                    day_night_score=str(row['day_night_score']) if pd.notna(row['day_night_score']) else '',
                    gender=str(row['gender']) if pd.notna(row['gender']) else 'Unisex',
                    sizes=str(row['sizes']) if pd.notna(row['sizes']) else '[]'
                )
                
                perfume.save()
                success_count += 1
                
                if success_count % 50 == 0:
                    print(f"진행률: {success_count}/{len(df)}")
                    
            except Exception as e:
                error_count += 1
                print(f"행 {index + 1} 처리 중 오류: {e}")
                # 에러가 발생해도 계속 진행
                continue
        
        print(f"\n데이터 로드 완료!")
        print(f"성공: {success_count}개")
        print(f"실패: {error_count}개")
        print(f"총 향수 개수: {Perfume.objects.count()}개")
        
    except Exception as e:
        print(f"CSV 파일 읽기 중 오류 발생: {e}")

def show_sample_data():
    """샘플 데이터 표시"""
    perfumes = Perfume.objects.all()[:5]
    
    print("\n=== 샘플 데이터 ===")
    for perfume in perfumes:
        print(f"브랜드: {perfume.brand}")
        print(f"이름: {perfume.name}")
        print(f"농도: {perfume.concentration}")
        print(f"성별: {perfume.gender}")
        print(f"톱노트: {perfume.top_notes}")
        print("-" * 50)

if __name__ == "__main__":
    print("향수 데이터 로더")
    print("=" * 50)
    
    load_perfume_data()
    show_sample_data()
