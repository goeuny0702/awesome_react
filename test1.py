import json
import time
import requests
from urllib.parse import quote

def get_coordinates(address):
    address = ' '.join(address.split())
    print(f"📍 재시도 주소: {address}")
    
    url = f"https://nominatim.openstreetmap.org/search?q={quote(address)}&format=json&limit=1"
    headers = {
        'User-Agent': 'ReactNativeApp/1.0 (zz4442@naver.com)'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result:
            lng = float(result[0]['lon'])
            lat = float(result[0]['lat'])
            print(f"✅ 성공: ({lng}, {lat})")
            return lng, lat
        else:
            print("❌ 여전히 좌표 없음")
            return None
    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return None

def retry_from_store():
    with open('assets/store.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    stores = data['stores']
    retried = []
    still_failed = []

    for store in stores:
        if 'lat' in store and 'lng' in store:
            continue  # 이미 좌표가 있음

        address = store.get('수정')
        if not address:
            continue

        coords = get_coordinates(address)
        if coords:
            lng, lat = coords
            store['lng'] = lng
            store['lat'] = lat
            retried.append(store)
        else:
            still_failed.append(store)

        time.sleep(1.2)

    # 다시 store.json 파일에 저장
    with open('assets/store.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 실패한 것만 따로 저장
    with open('assets/retry_failed.json', 'w', encoding='utf-8') as f:
        json.dump(still_failed, f, ensure_ascii=False, indent=2)

    print(f"\n📦 재시도 완료: 새로 성공 {len(retried)}개, 여전히 실패 {len(still_failed)}개")

if __name__ == "__main__":
    retry_from_store()
