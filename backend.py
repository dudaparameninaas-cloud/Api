from flask import Flask, request, jsonify, Response
import requests
import json
import os

app = Flask(__name__)

# JSON yanıtlarında Türkçe karakterleri ve okunaklılığı zorunlu kılar
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# API Ayarları
BASE_API_URL = "https://arastir.sbs/api"
PORT = int(os.environ.get('PORT', 5000))

def fix_turkish_chars(data):
    """
    Unicode kaçış dizilerini (örn: \u0130) gerçek karakterlere dönüştürür.
    """
    if data is None:
        return []
    if isinstance(data, (dict, list)):
        # dumps ve loads yaparak string içindeki kaçış dizilerini decode ederiz
        fixed_str = json.dumps(data, ensure_ascii=False, indent=2)
        return json.loads(fixed_str)
    return data

def pretty_json_response(data, status=200):
    """Okunaklı JSON response oluşturur"""
    return Response(
        response=json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        mimetype='application/json; charset=utf-8'
    )

def fetch_sulale_data(tc):
    """Sülale API'sinden veri çeker"""
    try:
        url = f"{BASE_API_URL}/sulale.php?tc={tc}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data
        return None
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

def filter_by_kinship(sulale_data, kinship_types):
    """Sülale verisinden istenen akrabalık tiplerini filtreler"""
    if not sulale_data or not isinstance(sulale_data, list):
        return []
    if isinstance(kinship_types, str):
        kinship_types = [kinship_types]
    
    filtered = [person for person in sulale_data if person.get('YAKINLIK') in kinship_types]
    return fix_turkish_chars(filtered)

@app.route('/', methods=['GET'])
def home():
    """Ana sayfa"""
    return pretty_json_response({
        "api": "Akrabalık Sorgulama API",
        "version": "2.0",
        "developer": "@ruslonder",
        "total_apis": 26,
        "status": "active",
        "encoding": "UTF-8 (Türkçe karakter desteği ✓)",
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
            response = requests.get(f"{BASE_API_URL}/sulale.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kendisi":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Kendisi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "cocuk":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Çocuğu")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "es":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Eşi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "anne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Annesi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "baba":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Babası")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kardes":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Kardeşi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "anneanne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Anneannesi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "babanne":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Babaannesi")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "dede":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, ["Dedesi", "Büyükbabası"])
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "amca-hala":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Amca/Hala")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "dayi-teyze":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, "Dayı/Teyze")
                return pretty_json_response(result)
            return pretty_json_response([])
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "kuzen":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            data = fetch_sulale_data(tc)
            if data:
                result = filter_by_kinship(data, ["Anne Tarafı Kuzen", "Baba Tarafı Kuzen"])
                return pretty_json_response(result)
            return pretty_json_response([])
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
                return pretty_json_response(fix_turkish_chars(akrabalar))
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
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "adres":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            response = requests.get(f"{BASE_API_URL}/adres.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "isyeri":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            response = requests.get(f"{BASE_API_URL}/isyeri.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "gsm-tc":
        gsm = request.args.get('gsm')
        if not gsm:
            return pretty_json_response({"error": "gsm parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            response = requests.get(f"{BASE_API_URL}/gsmtc.php?gsm={gsm}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "tc-gsm":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            response = requests.get(f"{BASE_API_URL}/tcgsm.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
        except Exception as e:
            return pretty_json_response({"error": str(e), "developer": "@ruslonder"}, 500)
    
    elif type_param == "tc":
        tc = request.args.get('tc')
        if not tc:
            return pretty_json_response({"error": "tc parametresi gerekli", "developer": "@ruslonder"}, 400)
        try:
            response = requests.get(f"{BASE_API_URL}/tc.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            raw_data = response.json()
            clean_data = fix_turkish_chars(raw_data)
            return pretty_json_response(clean_data)
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
        "encoding": "UTF-8"
    }, 200)

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     Akrabalık Sorgulama API v2.0 - JSON Okunaklı Versiyon   ║
    ║         Developer: @ruslonder                                ║
    ║         Tek API: /api?type=...                               ║
    ║         Toplam API Sayısı: 26                                ║
    ║         Türkçe Karakter Desteği: ✓                          ║
    ║         JSON Pretty Print: ✓                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    
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
