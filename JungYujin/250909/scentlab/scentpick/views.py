from django.shortcuts import render, get_object_or_404 
from .models import Perfume, Favorite, FeedbackEvent, NoteImage
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

# 노트 한국어 번역 딕셔너리
NOTE_TRANSLATIONS = {
    # Citrus Smells
    'Bergamot': '베르가못',
    'Bigarade': '비가라드',
    'Bitter Orange': '쓴오렌지',
    'Blood Orange': '블러드 오렌지',
    'Lemon': '레몬',
    'Lime': '라임',
    'Orange': '오렌지',
    'Grapefruit': '자몽',
    'Mandarin Orange': '만다린',
    'Tangerine': '탠저린',
    'Yuzu': '유자',
    'Neroli': '네롤리',
    'Petitgrain': '쁘띠그레인',
    'Citrus': '시트러스',
    'Lemongrass': '레몬그라스',
    
    # Fruits, Vegetables And Nuts
    'Apple': '사과',
    'Apricot': '살구',
    'Cherry': '체리',
    'Peach': '복숭아',
    'Pear': '배',
    'Plum': '자두',
    'Banana': '바나나',
    'Blackberry': '블랙베리',
    'Blueberry': '블루베리',
    'Raspberry': '라즈베리',
    'Strawberry': '딸기',
    'Black Currant': '블랙커런트',
    'Coconut': '코코넛',
    'Almond': '아몬드',
    'Walnut': '호두',
    'Hazelnut': '헤이즐넛',
    'Fig': '무화과',
    'Grape': '포도',
    'Watermelon': '수박',
    'Melon': '멜론',
    'Pineapple': '파인애플',
    'Mango': '망고',
    'Papaya': '파파야',
    'Passion Fruit': '패션프루트',
    'Kiwi': '키위',
    'Pomegranate': '석류',
    'Carrot': '당근',
    'Tomato': '토마토',
    
    # Flowers
    'Rose': '장미',
    'Jasmine': '자스민',
    'Lavender': '라벤더',
    'Lily': '백합',
    'Peony': '작약',
    'Gardenia': '치자꽃',
    'Tuberose': '튜베로즈',
    'Ylang-Ylang': '일랑일랑',
    'Carnation': '카네이션',
    'Violet': '제비꽃',
    'Iris': '아이리스',
    'Freesia': '프리지아',
    'Magnolia': '목련',
    'Lily of the Valley': '은방울꽃',
    'Geranium': '제라늄',
    'Narcissus': '수선화',
    'Orange Blossom': '오렌지 블라썸',
    'Lotus': '연꽃',
    'Mimosa': '미모사',
    'Honeysuckle': '인동꽃',
    'Wisteria': '등나무',
    'Hibiscus': '히비스커스',
    'Chamomile': '카모마일',
    'Marigold': '메리골드',
    'Sunflower': '해바라기',
    'Dahlia': '달리아',
    'Orchid': '난초',
    'Cherry Blossom': '벚꽃',
    'Plumeria': '플루메리아',
    'Lilac': '라일락',
    'Hyacinth': '히아신스',
    'Daffodil': '수선화',
    'Chrysanthemum': '국화',
    
    # Spices
    'Cinnamon': '계피',
    'Cardamom': '카다몬',
    'Clove': '정향',
    'Nutmeg': '육두구',
    'Black Pepper': '후추',
    'Pink Pepper': '핑크 페퍼',
    'Star Anise': '팔각',
    'Ginger': '생강',
    'Vanilla': '바닐라',
    'Saffron': '사프란',
    'Cumin': '커민',
    'Coriander': '고수',
    'Fennel': '회향',
    'Anise': '아니스',
    'Bay Leaf': '월계수',
    'Allspice': '올스파이스',
    'Turmeric': '강황',
    'Paprika': '파프리카',
    'Curry': '커리',
    
    # Woods
    'Sandalwood': '샌달우드',
    'Cedar': '시더',
    'Pine': '소나무',
    'Birch': '자작나무',
    'Oak': '참나무',
    'Bamboo': '대나무',
    'Driftwood': '유목',
    'Ebony': '흑단',
    'Mahogany': '마호가니',
    'Rosewood': '로즈우드',
    'Teak': '티크',
    'Cypress': '사이프러스',
    'Juniper': '주니퍼',
    'Fir': '전나무',
    'Spruce': '가문비나무',
    'Elm': '느릅나무',
    'Ash': '물푸레나무',
    'Maple': '단풍나무',
    'Cherry Wood': '체리우드',
    'Apple Wood': '사과나무',
    'Olive Wood': '올리브 나무',
    
    # Resins
    'Amber': '앰버',
    'Frankincense': '프랑킨센스',
    'Myrrh': '몰약',
    'Benzoin': '벤조인',
    'Labdanum': '라브다눔',
    'Opoponax': '오포포낙스',
    'Elemi': '엘레미',
    'Copal': '코팔',
    'Dragon Blood': '드래곤 블러드',
    'Styrax': '스티락스',
    
    # Musks and Animal notes
    'Musk': '머스크',
    'White Musk': '화이트 머스크',
    'Ambergris': '앰버그리스',
    'Civet': '시벳',
    'Castoreum': '카스토리움',
    'Ambroxan': '암브록산',
    'Iso E Super': '이소 E 슈퍼',
    
    # Green and Aromatic
    'Mint': '민트',
    'Basil': '바질',
    'Thyme': '타임',
    'Rosemary': '로즈마리',
    'Sage': '세이지',
    'Oregano': '오레가노',
    'Marjoram': '마조람',
    'Eucalyptus': '유칼립투스',
    'Tea Tree': '티트리',
    'Pine Needles': '솔잎',
    'Grass': '풀',
    'Moss': '이끼',
    'Fern': '고사리',
    'Leaves': '잎',
    'Green Notes': '그린 노트',
    'Seaweed': '해조류',
    'Algae': '조류',
    
    # Gourmand and Sweet
    'Chocolate': '초콜릿',
    'Coffee': '커피',
    'Caramel': '카라멜',
    'Honey': '꿀',
    'Sugar': '설탕',
    'Cream': '크림',
    'Milk': '우유',
    'Butter': '버터',
    'Bread': '빵',
    'Cookie': '쿠키',
    'Cake': '케이크',
    'Pie': '파이',
    'Jam': '잼',
    'Maple Syrup': '메이플 시럽',
    'Marshmallow': '마시멜로',
    'Cotton Candy': '솜사탕',
    'Liquorice': '감초',
    'Praline': '프랄린',
    'Nougat': '누가',
    'Toffee': '토피',
    'Fudge': '퍼지',
    
    # Alcoholic beverages
    'Wine': '와인',
    'Champagne': '샴페인',
    'Whiskey': '위스키',
    'Rum': '럼',
    'Brandy': '브랜디',
    'Gin': '진',
    'Vodka': '보드카',
    'Beer': '맥주',
    'Sake': '사케',
    'Cognac': '코냑',
    
    # Tea and Tobacco
    'Black Tea': '홍차',
    'Green Tea': '녹차',
    'White Tea': '백차',
    'Oolong Tea': '우롱차',
    'Earl Grey': '얼그레이',
    'Jasmine Tea': '자스민차',
    'Chai': '차이',
    'Tobacco': '담배',
    'Pipe Tobacco': '파이프 담배',
    'Cigarette': '담배',
    'Cuban Tobacco': '쿠바 담배',
    
    # Marine and Aquatic
    'Sea Water': '바닷물',
    'Ocean Breeze': '바다 바람',
    'Salt': '소금',
    'Seashells': '조개껍질',
    'Coral': '산호',
    'Driftwood': '유목',
    'Kelp': '다시마',
    'Plankton': '플랑크톤',
    'Rain': '비',
    'Water': '물',
    'Ice': '얼음',
    'Snow': '눈',
    'Fog': '안개',
    'Ozone': '오존',
    
    # Leather and Animalic
    'Leather': '가죽',
    'Suede': '스웨이드',
    'Fur': '모피',
    'Skin': '피부',
    'Hair': '머리카락',
    'Sweat': '땀',
    'Body Odor': '체취',
    
    # Metallic and Mineral
    'Metal': '금속',
    'Iron': '철',
    'Steel': '강철',
    'Copper': '구리',
    'Silver': '은',
    'Gold': '금',
    'Tin': '주석',
    'Lead': '납',
    'Stone': '돌',
    'Flint': '부싯돌',
    'Concrete': '콘크리트',
    'Dust': '먼지',
    'Sand': '모래',
    'Clay': '점토',
    'Chalk': '분필',
    'Gunpowder': '화약',
    'Sulfur': '황',
    'Tar': '타르',
    'Gasoline': '휘발유',
    'Rubber': '고무',
    'Plastic': '플라스틱',
}

def get_korean_note_name(english_name):
    """영어 노트명을 한국어로 번역"""
    return NOTE_TRANSLATIONS.get(english_name, english_name)

# 한국어 → 영어 역번역 딕셔너리
KOREAN_TO_ENGLISH = {
    '베르가못': 'Bergamot',
    '비가라드': 'Bigarade',
    '쓴오렌지': 'Bitter Orange',
    '블러드오렌지': 'Blood Orange',
    '레몬': 'Lemon',
    '라임': 'Lime',
    '오렌지': 'Orange',
    '자몽': 'Grapefruit',
    '만다린': 'Mandarin Orange',
    '탠저린': 'Tangerine',
    '유자': 'Yuzu',
    '네롤리': 'Neroli',
    '쁘띠그레인': 'Petitgrain',
    '시트러스': 'Citrus',
    '레몬그라스': 'Lemongrass',
    
    # 과일
    '사과': 'Apple',
    '살구': 'Apricot',
    '체리': 'Cherry',
    '복숭아': 'Peach',
    '배': 'Pear',
    '자두': 'Plum',
    '바나나': 'Banana',
    '블랙베리': 'Blackberry',
    '블루베리': 'Blueberry',
    '라즈베리': 'Raspberry',
    '딸기': 'Strawberry',
    '블랙커런트': 'Black Currant',
    '커런트': 'Black Currant',
    '코코넛': 'Coconut',
    '아몬드': 'Almond',
    '호두': 'Walnut',
    '헤이즐넛': 'Hazelnut',
    '무화과': 'Fig',
    '포도': 'Grape',
    '수박': 'Watermelon',
    '멜론': 'Melon',
    '파인애플': 'Pineapple',
    '망고': 'Mango',
    '파파야': 'Papaya',
    '패션프루트': 'Passion Fruit',
    '키위': 'Kiwi',
    '석류': 'Pomegranate',
    '당근': 'Carrot',
    '토마토': 'Tomato',
    '리치': 'Lychee',
    
    # 꽃
    '장미': 'Rose',
    '로즈': 'Rose',
    '자스민': 'Jasmine',
    '라벤더': 'Lavender',
    '백합': 'Lily',
    '작약': 'Peony',
    '피오니': 'Peony',
    '치자꽃': 'Gardenia',
    '튜베로즈': 'Tuberose',
    '일랑일랑': 'Ylang-Ylang',
    '카네이션': 'Carnation',
    '제비꽃': 'Violet',
    '바이올렛': 'Violet',
    '아이리스': 'Iris',
    '프리지아': 'Freesia',
    '목련': 'Magnolia',
    '매그놀리아': 'Magnolia',
    '은방울꽃': 'Lily of the Valley',
    '제라늄': 'Geranium',
    '수선화': 'Narcissus',
    '오렌지블라썸': 'Orange Blossom',
    '연꽃': 'Lotus',
    '미모사': 'Mimosa',
    '인동꽃': 'Honeysuckle',
    '등나무': 'Wisteria',
    '히비스커스': 'Hibiscus',
    '카모마일': 'Chamomile',
    '메리골드': 'Marigold',
    '해바라기': 'Sunflower',
    '달리아': 'Dahlia',
    '난초': 'Orchid',
    '벚꽃': 'Cherry Blossom',
    '플루메리아': 'Plumeria',
    '라일락': 'Lilac',
    '히아신스': 'Hyacinth',
    '국화': 'Chrysanthemum',
    
    # 스파이스
    '계피': 'Cinnamon',
    '카다몬': 'Cardamom',
    '정향': 'Clove',
    '육두구': 'Nutmeg',
    '후추': 'Black Pepper',
    '핑크페퍼': 'Pink Pepper',
    '핑크': 'Pink Pepper',
    '페퍼': 'Pepper',
    '팔각': 'Star Anise',
    '생강': 'Ginger',
    '바닐라': 'Vanilla',
    '사프란': 'Saffron',
    '커민': 'Cumin',
    '고수': 'Coriander',
    '코리안더': 'Coriander',
    '회향': 'Fennel',
    '아니스': 'Anise',
    '월계수': 'Bay Leaf',
    '올스파이스': 'Allspice',
    '강황': 'Turmeric',
    '파프리카': 'Paprika',
    '커리': 'Curry',
    
    # 우드
    '샌달우드': 'Sandalwood',
    '시더': 'Cedar',
    '소나무': 'Pine',
    '자작나무': 'Birch',
    '참나무': 'Oak',
    '대나무': 'Bamboo',
    '유목': 'Driftwood',
    '흑단': 'Ebony',
    '마호가니': 'Mahogany',
    '로즈우드': 'Rosewood',
    '팰리샌더': 'Rosewood',
    '티크': 'Teak',
    '사이프러스': 'Cypress',
    '시프레': 'Cypress',
    '주니퍼': 'Juniper',
    '전나무': 'Fir',
    '가문비나무': 'Spruce',
    '느릅나무': 'Elm',
    '물푸레나무': 'Ash',
    '단풍나무': 'Maple',
    '체리우드': 'Cherry Wood',
    '사과나무': 'Apple Wood',
    '올리브나무': 'Olive Wood',
    '우디': 'Woody',
    '노트': 'Notes',
    
    # 레진
    '앰버': 'Amber',
    '프랑킨센스': 'Frankincense',
    '몰약': 'Myrrh',
    '벤조인': 'Benzoin',
    '라브다눔': 'Labdanum',
    '오포포낙스': 'Opoponax',
    '엘레미': 'Elemi',
    '코팔': 'Copal',
    '드래곤블러드': 'Dragon Blood',
    '스티락스': 'Styrax',
    
    # 머스크
    '머스크': 'Musk',
    '화이트머스크': 'White Musk',
    '화이트': 'White',
    '앰버그리스': 'Ambergris',
    '시벳': 'Civet',
    '카스토리움': 'Castoreum',
    '암브록산': 'Ambroxan',
    '이소이수퍼': 'Iso E Super',
    
    # 그린/아로마틱
    '민트': 'Mint',
    '바질': 'Basil',
    '타임': 'Thyme',
    '로즈마리': 'Rosemary',
    '세이지': 'Sage',
    '오레가노': 'Oregano',
    '마조람': 'Marjoram',
    '유칼립투스': 'Eucalyptus',
    '티트리': 'Tea Tree',
    '솔잎': 'Pine Needles',
    '풀': 'Grass',
    '이끼': 'Moss',
    '모스': 'Moss',
    '고사리': 'Fern',
    '잎': 'Leaves',
    '그린노트': 'Green Notes',
    '해조류': 'Seaweed',
    '조류': 'Algae',
    
    # 구르망/스위트
    '초콜릿': 'Chocolate',
    '커피': 'Coffee',
    '카라멜': 'Caramel',
    '꿀': 'Honey',
    '허니': 'Honey',
    '설탕': 'Sugar',
    '크림': 'Cream',
    '우유': 'Milk',
    '버터': 'Butter',
    '빵': 'Bread',
    '쿠키': 'Cookie',
    '케이크': 'Cake',
    '파이': 'Pie',
    '잼': 'Jam',
    '메이플시럽': 'Maple Syrup',
    '마시멜로': 'Marshmallow',
    '솜사탕': 'Cotton Candy',
    '감초': 'Liquorice',
    '프랄린': 'Praline',
    '누가': 'Nougat',
    '토피': 'Toffee',
    '퍼지': 'Fudge',
    
    # 음료
    '와인': 'Wine',
    '샴페인': 'Champagne',
    '위스키': 'Whiskey',
    '럼': 'Rum',
    '브랜디': 'Brandy',
    '진': 'Gin',
    '보드카': 'Vodka',
    '맥주': 'Beer',
    '사케': 'Sake',
    '코냑': 'Cognac',
    
    # 차/담배
    '홍차': 'Black Tea',
    '녹차': 'Green Tea',
    '백차': 'White Tea',
    '우롱차': 'Oolong Tea',
    '얼그레이': 'Earl Grey',
    '자스민차': 'Jasmine Tea',
    '차이': 'Chai',
    '담배': 'Tobacco',
    '파이프담배': 'Pipe Tobacco',
    '쿠바담배': 'Cuban Tobacco',
    
    # 해양/아쿠아틱
    '바닷물': 'Sea Water',
    '바다바람': 'Ocean Breeze',
    '소금': 'Salt',
    '조개껍질': 'Seashells',
    '산호': 'Coral',
    '다시마': 'Kelp',
    '플랑크톤': 'Plankton',
    '비': 'Rain',
    '물': 'Water',
    '얼음': 'Ice',
    '눈': 'Snow',
    '안개': 'Fog',
    '오존': 'Ozone',
    
    # 가죽/애니멀릭
    '가죽': 'Leather',
    '레더': 'Leather',
    '스웨이드': 'Suede',
    '모피': 'Fur',
    '피부': 'Skin',
    '머리카락': 'Hair',
    '땀': 'Sweat',
    '체취': 'Body Odor',
    
    # 기타 자주 나오는 노트들
    '페출리': 'Patchouli',
    '파츌리': 'Patchouli',
    '페출': 'Patchouli',
    '베티버': 'Vetiver',
    '카시스': 'Black Currant',
    '블랙': 'Black',
    '다마스크': 'Damask',
    '불가리안': 'Bulgarian',
    '터키쉬': 'Turkish',
    '스파이스': 'Spice',
    '루트': 'Root',
    '시앗': 'Seed',
    '씨앗': 'Seed',
    '알데하이드': 'Aldehyde',
    '부들레아': 'Buddleia',
    '월': 'Month',
    '5월의': 'May',
    '페탈': 'Petal',
    '워': 'Water',
}

def get_english_note_name(korean_name):
    """한국어 노트명을 영어로 역번역"""
    return KOREAN_TO_ENGLISH.get(korean_name, korean_name)

def get_note_image_url(note_name):
    """노트명으로 이미지 URL 가져오기 - 개선된 버전"""
    try:
        # 한국어면 영어로 변환
        english_name = get_english_note_name(note_name)
        
        print(f"Debug: 노트명 '{note_name}' -> 영어명 '{english_name}'")  # 디버깅용
        
        # 1. 정확한 이름으로 검색
        note_image = NoteImage.objects.filter(note_name__iexact=english_name).first()
        if note_image:
            print(f"Debug: 정확히 매칭됨 - {note_image.image_url}")
            return note_image.image_url
        
        # 2. 부분 매칭으로 검색 (대소문자 무시)
        note_image = NoteImage.objects.filter(note_name__icontains=english_name).first()
        if note_image:
            print(f"Debug: 부분 매칭됨 - {note_image.image_url}")
            return note_image.image_url
        
        # 3. 공백으로 분리해서 각 단어로 검색
        if ' ' in english_name:
            for word in english_name.split():
                if len(word) > 2:  # 2글자 이상인 단어만
                    note_image = NoteImage.objects.filter(note_name__icontains=word).first()
                    if note_image:
                        print(f"Debug: 단어 '{word}'로 매칭됨 - {note_image.image_url}")
                        return note_image.image_url
        
        # 4. 역방향 검색 - DB의 노트명이 한국어 노트명을 포함하는지
        notes_containing = NoteImage.objects.filter(note_name__icontains=note_name).first()
        if notes_containing:
            print(f"Debug: 역방향 매칭됨 - {notes_containing.image_url}")
            return notes_containing.image_url
            
        print(f"Debug: 매칭 실패 - '{note_name}' ('{english_name}')")
        return None
        
    except Exception as e:
        print(f"Error getting note image for {note_name}: {e}")
        return None

# product_detail 함수 수정

def product_detail(request, perfume_id):
    # DB 테스트 (개발용 - 나중에 제거)
    test_note_images()
    
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
    
    # 노트에 이미지 URL과 한국어 이름 추가
    def enhance_notes(notes_list):
        enhanced_notes = []
        for note in notes_list:
            enhanced_notes.append({
                'name': note,
                'korean_name': note,  # 이미 한국어이므로 그대로 사용
                'image_url': get_note_image_url(note)  # 한국어→영어 변환 후 이미지 검색
            })
        return enhanced_notes
    
    enhanced_top_notes = enhance_notes(top_notes)
    enhanced_middle_notes = enhance_notes(middle_notes)
    enhanced_base_notes = enhance_notes(base_notes)
    
    # 이전/다음 향수 가져오기
    prev_perfume = Perfume.objects.filter(id__lt=perfume_id).order_by('-id').first()
    next_perfume = Perfume.objects.filter(id__gt=perfume_id).order_by('id').first()

    context = {
        'perfume': perfume,
        'image_url': image_url,
        'main_accords': main_accords,
        'top_notes': enhanced_top_notes,
        'middle_notes': enhanced_middle_notes,
        'base_notes': enhanced_base_notes,
        'sizes': perfume.sizes,
        'gender': perfume.gender,
        'prev_perfume': prev_perfume,
        'next_perfume': next_perfume,
    }
    return render(request, 'scentpick/product_detail.html', context)

@require_POST
def toggle_favorite(request):
    """즐겨찾기 토글 - admin 사용자 사용 (디버깅 추가)"""
    try:
        data = json.loads(request.body)
        perfume_id = data.get('perfume_id')
        
        print(f"DEBUG: 받은 perfume_id = {perfume_id}")  # 디버깅
        
        if not perfume_id:
            return JsonResponse({
                'status': 'error',
                'message': '향수 ID가 필요합니다.'
            }, status=400)
        
        perfume = get_object_or_404(Perfume, id=perfume_id)
        print(f"DEBUG: 찾은 향수 = {perfume.name}")  # 디버깅
        
        # admin 사용자 사용
        from django.contrib.auth.models import User
        admin_user = User.objects.get(username='playdata2')
        print(f"DEBUG: admin_user ID = {admin_user.id}")  # 디버깅
        
        # DB에서 즐겨찾기 확인
        favorite = Favorite.objects.filter(
            user=admin_user,
            perfume=perfume
        ).first()
        
        if favorite:
            # 즐겨찾기에서 제거
            favorite.delete()
            is_favorite = False
            message = f'{perfume.name}이(가) 즐겨찾기에서 제거되었습니다.'
            print(f"DEBUG: 즐겨찾기 제거됨")  # 디버깅
        else:
            # 즐겨찾기에 추가
            new_favorite = Favorite.objects.create(
                user=admin_user,
                perfume=perfume
            )
            is_favorite = True
            message = f'{perfume.name}이(가) 즐겨찾기에 추가되었습니다.'
            print(f"DEBUG: 즐겨찾기 추가됨 - ID: {new_favorite.id}")  # 디버깅
        
        # 현재 즐겨찾기 개수 확인
        total_favorites = Favorite.objects.filter(user=admin_user).count()
        print(f"DEBUG: 총 즐겨찾기 개수 = {total_favorites}")  # 디버깅
        
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'message': message,
            'debug_total_favorites': total_favorites  # 디버깅 정보
        })
        
    except User.DoesNotExist:
        print("DEBUG: playdata2 사용자를 찾을 수 없음")  # 디버깅
        return JsonResponse({
            'status': 'error',
            'message': 'admin 사용자를 찾을 수 없습니다.'
        }, status=500)
    except Exception as e:
        print(f"DEBUG: 오류 발생 - {str(e)}")  # 디버깅
        return JsonResponse({
            'status': 'error',
            'message': f'오류가 발생했습니다: {str(e)}'
        }, status=500)

@require_POST
def toggle_like_dislike(request):
    """좋아요/싫어요 토글 - admin 사용자 사용 (디버깅 추가)"""
    try:
        data = json.loads(request.body)
        perfume_id = data.get('perfume_id')
        action = data.get('action')  # 'like' 또는 'dislike'
        
        print(f"DEBUG: 받은 perfume_id = {perfume_id}, action = {action}")  # 디버깅
        
        if not perfume_id or action not in ['like', 'dislike']:
            return JsonResponse({
                'status': 'error',
                'message': '유효하지 않은 요청입니다.'
            }, status=400)
        
        perfume = get_object_or_404(Perfume, id=perfume_id)
        print(f"DEBUG: 찾은 향수 = {perfume.name}")  # 디버깅
        
        # admin 사용자 사용
        from django.contrib.auth.models import User
        admin_user = User.objects.get(username='playdata2')
        print(f"DEBUG: admin_user ID = {admin_user.id}")  # 디버깅
        
        # 기존 피드백 이벤트 확인
        existing_feedback = FeedbackEvent.objects.filter(
            user=admin_user,
            perfume=perfume,
            action__in=['like', 'dislike']
        ).first()
        
        if existing_feedback:
            print(f"DEBUG: 기존 피드백 있음 - {existing_feedback.action}")  # 디버깅
            if existing_feedback.action == action:
                # 같은 액션이면 삭제 (토글 off)
                existing_feedback.delete()
                current_action = None
                message = f'{perfume.name}의 {action}가 취소되었습니다.'
                print(f"DEBUG: 피드백 삭제됨")  # 디버깅
            else:
                # 다른 액션이면 업데이트 (좋아요 ↔ 싫어요)
                existing_feedback.action = action
                existing_feedback.save()
                current_action = action
                if action == 'like':
                    message = f'{perfume.name}에 좋아요를 눌렀습니다!'
                else:
                    message = f'{perfume.name}에 싫어요를 눌렀습니다.'
                print(f"DEBUG: 피드백 업데이트됨 - {action}")  # 디버깅
        else:
            # 새로운 피드백 이벤트 생성
            new_feedback = FeedbackEvent.objects.create(
                user=admin_user,
                perfume=perfume,
                action=action,
                source='detail',
                context={'page': 'product_detail', 'user': 'admin'}
            )
            current_action = action
            if action == 'like':
                message = f'{perfume.name}에 좋아요를 눌렀습니다!'
            else:
                message = f'{perfume.name}에 싫어요를 눌렀습니다.'
            print(f"DEBUG: 새 피드백 생성됨 - ID: {new_feedback.id}, action: {action}")  # 디버깅
        
        # 현재 피드백 상태 확인
        total_likes = FeedbackEvent.objects.filter(user=admin_user, action='like').count()
        total_dislikes = FeedbackEvent.objects.filter(user=admin_user, action='dislike').count()
        print(f"DEBUG: 총 좋아요 = {total_likes}, 총 싫어요 = {total_dislikes}")  # 디버깅
        
        return JsonResponse({
            'status': 'success',
            'current_action': current_action,
            'message': message,
            'debug_likes': total_likes,
            'debug_dislikes': total_dislikes
        })
        
    except User.DoesNotExist:
        print("DEBUG: playdata2 사용자를 찾을 수 없음")  # 디버깅
        return JsonResponse({
            'status': 'error',
            'message': 'admin 사용자를 찾을 수 없습니다.'
        }, status=500)
    except Exception as e:
        print(f"DEBUG: 오류 발생 - {str(e)}")  # 디버깅
        return JsonResponse({
            'status': 'error',
            'message': f'오류가 발생했습니다: {str(e)}'
        }, status=500)

def offlines(request):
    return render(request, "scentpick/offlines.html")

# @login_required  # 주석처리 - 로그인 기능
def mypage(request):
    """마이페이지 - admin 사용자 기반"""
    try:
        from django.contrib.auth.models import User
        admin_user = User.objects.get(username='playdata2')
        
        # admin 사용자의 즐겨찾기한 향수들 가져오기
        favorite_perfumes = Perfume.objects.filter(
            favorited_by__user=admin_user
        ).order_by('-favorited_by__created_at')
        
        # admin 사용자의 좋아요한 향수들 가져오기
        liked_perfumes = Perfume.objects.filter(
            feedback_events__user=admin_user,
            feedback_events__action='like'
        ).distinct().order_by('-feedback_events__created_at')
        
        # admin 사용자의 싫어요한 향수들 가져오기
        disliked_perfumes = Perfume.objects.filter(
            feedback_events__user=admin_user,
            feedback_events__action='dislike'
        ).distinct().order_by('-feedback_events__created_at')
        
        favorites_count = favorite_perfumes.count()
        likes_count = liked_perfumes.count()
        dislikes_count = disliked_perfumes.count()
        
        context = {
            'favorite_perfumes': favorite_perfumes,
            'favorites_count': favorites_count,
            'liked_perfumes': liked_perfumes,
            'likes_count': likes_count,
            'disliked_perfumes': disliked_perfumes,
            'dislikes_count': dislikes_count
        }
        
    except User.DoesNotExist:
        context = {
            'favorite_perfumes': Perfume.objects.none(),
            'favorites_count': 0,
            'liked_perfumes': Perfume.objects.none(),
            'likes_count': 0,
            'disliked_perfumes': Perfume.objects.none(),
            'dislikes_count': 0,
            'error': 'admin 사용자를 찾을 수 없습니다.'
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

def test_note_images():
    """DB에 note_images 데이터가 제대로 들어있는지 테스트"""
    try:
        total_count = NoteImage.objects.count()
        print(f"총 노트 이미지 개수: {total_count}")
        
        # 몇 개 샘플 출력
        samples = NoteImage.objects.all()[:10]
        for sample in samples:
            print(f"카테고리: {sample.category}, 노트명: {sample.note_name}, URL: {sample.image_url}")
            
        # 특정 노트들 검색 테스트
        test_notes = ['Rose', 'Lemon', 'Orange', 'Bergamot', 'Jasmine']
        for note in test_notes:
            found = NoteImage.objects.filter(note_name__iexact=note).first()
            print(f"'{note}' 검색 결과: {found.note_name if found else '없음'}")
            
    except Exception as e:
        print(f"DB 테스트 에러: {e}")

