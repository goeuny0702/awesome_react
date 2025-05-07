import json
import time
import sys
import requests
from urllib.parse import quote

# 🔍 좌표 얻는 함수
def get_coordinates(address):
    address = ' '.join(address.split())  # 공백 정리
    print(f"📍 검색할 주소: {address}")
    
    url = f"https://nominatim.openstreetmap.org/search?q={quote(address)}&format=json&limit=1"
    headers = {
        'User-Agent': 'ReactNativeApp/1.0 (zz4442@naver.com)'  # ← 여기에 너 이메일 넣어줘!
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 403 같은 에러 잡기
        result = response.json()
        
        if result:
            lng = float(result[0]['lon'])
            lat = float(result[0]['lat'])
            print(f"✅ 좌표 찾음: ({lng}, {lat})")
            return lng, lat
        else:
            print("❌ 좌표 결과 없음")
            return None
    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return None

# 진행률 출력
def print_progress(current, total):
    bar_length = 40
    progress = current / total
    block = int(bar_length * progress)
    text = f"\r📦 진행률: [{'■' * block}{'□' * (bar_length - block)}] {current}/{total} 완료"
    sys.stdout.write(text)
    sys.stdout.flush()

# 메인 로직
def main():
    with open('assets/store.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    stores = data['stores']
    total_stores = len(stores)
    failed_stores = []

    for idx, store in enumerate(stores, 1):
        address = store.get('수정')

        if not address:
            print(f"\n[건너뜀] {store.get('가맹점명', '알 수 없음')} - '수정' 키 없음")
            continue

        coords = get_coordinates(address)

        if coords:
            lng, lat = coords
            store['lng'] = lng
            store['lat'] = lat
            print(f"\n[성공] {store['가맹점명']} - 좌표 추가됨")
        else:
            print(f"\n[실패] {store['가맹점명']} - 좌표 찾기 실패")
            failed_stores.append({
                '가맹점명': store.get('가맹점명', '알 수 없음'),
                '주소': address
            })

        time.sleep(1.2)  # API 요청 간 딜레이 (중요!)
        print_progress(idx, total_stores)

    # 저장
    with open('assets/store.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if failed_stores:
        with open('assets/failed_stores.json', 'w', encoding='utf-8') as f:
            json.dump(failed_stores, f, ensure_ascii=False, indent=2)
        print(f"\n\n❗ 실패한 가게 {len(failed_stores)}개 → assets/failed_stores.json 저장됨")

    print("\n\n✅ 모든 좌표 추출 완료! → assets/store.json에 반영됨")

if __name__ == "__main__":
    main()
