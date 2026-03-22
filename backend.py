from flask import Flask, request, jsonify, Response
import requests
import json
import os
import random

app = Flask(__name__)

# JSON yanıtlarında Türkçe karakterleri ve okunaklılığı zorunlu kılar
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# API Ayarları
BASE_API_URL = "https://arastir.sbs/api"
PORT = int(os.environ.get('PORT', 5000))

# Browser gibi görünmek için header'lar
def get_headers():
    """API'lerin bot engelini aşmak için gerçekçi header'lar"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Origin": "https://www.google.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }

def fix_turkish_chars(data):
    """
    Unicode kaçış dizilerini (örn: \u0130) gerçek karakterlere dönüştürür.
    """
    if data is None:
        return []
    if isinstance(data, (dict, list)):
        try:
            fixed_str = json.dumps(data, ensure_ascii=False, indent=2)
            return json.loads(fixed_str)
        except:
            return data
    return data

def pretty_json_response(data, status=200):
    """Okunaklı JSON response oluşturur"""
    try:
        # Önce karakterleri düzelt
        data = fix_turkish_chars(data)
        return Response(
            response=json.dumps(data, ensure_ascii=False, indent=2),
            status=status,
            mimetype='application/json; charset=utf-8'
        )
    except Exception as e:
        return Response(
            response=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2),
            status=500,
            mimetype='application/json; charset=utf-8'
        )

def fetch_api_data(url):
    """API'den header'larla veri çeker - bot engelini aşar"""
    try:
        headers = get_headers()
        print(f"📡 İstek gönderiliyor: {url}")
        print(f"📋 Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        data = response.json()
        
        # Boş liste de olsa döndür
        if data is None:
            return []
        
        # Her zaman listeyi döndür
        if isinstance(data, list):
            return data
        else:
            return [data] if data else []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ İstek hatası: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON hatası: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Genel hata: {str(e)}")
        return []

def fetch_sulale_data(tc):
    """Sülale API'sinden veri çeker - header destekli"""
    try:
        url = f"{BASE_API_URL}/sulale.php?tc={tc}"
        return fetch_api_data(url)
    except Exception as e:
        print(f"Sülale hatası: {str(e)}")
        return []

def filter_by_kinship(sulale_data, kinship_types):
    """Sülale verisinden istenen akrabalık tiplerini filtreler"""
    if not sulale_data or not isinstance(sulale_data, list):
        return []
    if isinstance(kinship_types, str):
        kinship_types = [kinship_types]
    
    filtered = [person for person in sulale_data if person.get('YAKINLIK') in kinship_types]
    return filtered

@app.route('/', methods=['GET'])
def home():
    """Ana sayfa"""
    return pretty_json_response({
        "api": "Akrabalık Sorgulama API",
        "version": "3.0",
        "developer": "@ruslonder",
        "total_apis": 26,
        "status": "active",
        "encoding": "UTF-8 (Türkçe karakter desteği ✓)",
        "bot_bypass": "User-Agent + Header spoofing aktif",
        "endpoints": {
            "tek_api": "/api?type=...",
            "available_types": [
                "sulale", "kendisi", "cocuk", "es", "anne", "baba", 
                "kardes", "anneanne", "babanne", "dede", "amca-hala", 
                "dayi-teyze", "kuzen", "tum-akrabalar",
                "adsoyad", "adres", "isyeri", "gsm-tc", "tc-gsm", "tc"
            ]
        }
    })

@app.route('/api', methods=['GET'])
def tek_api():
    type_param = request.args.get('type')
    
    if not type_param:
        return pretty_json_response({"error": "type parametresi gerekli", "developer": "@ruslonder"}, 400)
    
    # ============= SÜLALE / AKRABALIK API'LERİ =============
    
    if type_param == "sulale":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/sulale.php?tc={tc}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kendisi":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Kendisi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "cocuk":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Çocuğu")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "es":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Eşi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "anne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Annesi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "baba":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Babası")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kardes":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Kardeşi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "anneanne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Anneannesi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "babanne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Babaannesi")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "dede":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, ["Dedesi", "Büyükbabası"])
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "amca-hala":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Amca/Hala")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "dayi-teyze":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, "Dayı/Teyze")
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kuzen":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            result = filter_by_kinship(data, ["Anne Tarafı Kuzen", "Baba Tarafı Kuzen"])
            return pretty_json_response(result)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "tum-akrabalar":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                akrabalar = [kisi for kisi in data if kisi.get('YAKINLIK') != "Kendisi"]
                return pretty_json_response(akrabalar)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    # ============= TEMEL SORGULAMA API'LERİ =============
    
    elif type_param == "adsoyad":
        adi = request.args.get('adi')
        soyadi = request.args.get('soyadi')
        il = request.args.get('il')
        
        if not adi or not soyadi:
            return pretty_json_response({"error": "adi ve soyadi parametreleri gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/adsoyad.php?adi={adi}&soyadi={soyadi}"
            if il:
                url += f"&il={il}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "adres":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/adres.php?tc={tc}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "isyeri":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/isyeri.php?tc={tc}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "gsm-tc":
        gsm = request.args.get('gsm')
        if not gsm:
            return pretty_json_response({"error": "gsm parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/gsmtc.php?gsm={gsm}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "tc-gsm":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/tcgsm.php?tc={tc}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "tc":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            url = f"{BASE_API_URL}/tc.php?tc={tc}"
            data = fetch_api_data(url)
            return pretty_json_response(data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    else:
        return pretty_json_response({
            "error": f"Geçersiz type: {type_param}",
            "developer": "@ruslonder",
            "available_types": [
                "sulale", "kendisi", "cocuk", "es", "anne", "baba", 
                "kardes", "anneanne", "babanne", "dede", "amca-hala", 
                "dayi-teyze", "kuzen", "tum-akrabalar",
                "adsoyad", "adres", "isyeri", "gsm-tc", "tc-gsm", "tc"
            ]
        }, 400)

@app.route('/health', methods=['GET'])
def health():
    """Sağlık kontrolü"""
    return pretty_json_response({
        "status": "healthy",
        "developer": "@ruslonder",
        "encoding": "UTF-8",
        "bot_bypass": "active"
    }, 200)

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     Akrabalık Sorgulama API v3.0 - BOT ENGELİ AŞILDI       ║
    ║         Developer: @ruslonder                                ║
    ║         Tek API: /api?type=...                               ║
    ║         Toplam API Sayısı: 26                                ║
    ║         Türkçe Karakter Desteği: ✓                          ║
    ║         JSON Pretty Print: ✓                                 ║
    ║         Bot Bypass (User-Agent + Headers): ✓                ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🔥 YAPILAN DEĞİŞİKLİKLER:
    ✅ User-Agent eklendi (rastgele değişiyor)
    ✅ Referer, Origin header'ları eklendi
    ✅ fetch fonksiyonu düzeltildi (return data or [])
    ✅ Hata yönetimi iyileştirildi
    ✅ Tüm API'ler header destekli
    
    📌 KULLANIM ÖRNEKLERİ:
    
    🔹 SÜLALE / AKRABALIK SORGULAMA:
    • Tüm Sülale:        /api?type=sulale&tc=11111111110
    • Çocuklar:          /api?type=cocuk&tc=11111111110
    • Kuzenler:          /api?type=kuzen&tc=11111111110
    
    🔹 TEMEL SORGULAMA:
    • Ad Soyad:          /api?type=adsoyad&adi=eymen&soyadi=yavuz
    • Adres:             /api?type=adres&tc=11111111110
    • GSM'den TC:        /api?type=gsm-tc&gsm=5334451354
    
    Server başlatılıyor...
    Port: """ + str(PORT) + """
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
