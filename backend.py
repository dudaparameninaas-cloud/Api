from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# JSON yanıtlarında Türkçe karakterleri düzgün göstermek için
app.config['JSON_AS_ASCII'] = False

# Ana API URL
BASE_API_URL = "https://arastir.sbs/api"

# Render için port ayarı
PORT = int(os.environ.get('PORT', 5000))

@app.route('/', methods=['GET'])
def home():
    """Ana sayfa"""
    return jsonify({
        "api": "Akrabalık Sorgulama API",
        "version": "2.0",
        "developer": "@ruslonder",
        "total_apis": 26,
        "status": "active",
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

# ============= SÜLALE (AKRABALIK) FONKSİYONLARI =============

def fetch_sulale_data(tc):
    """Sülale API'sinden veri çeker"""
    try:
        response = requests.get(f"{BASE_API_URL}/sulale.php?tc={tc}", timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data
        return None
    except Exception as e:
        return None

def filter_by_kinship(sulale_data, kinship_types):
    """Sülale verisinden istenen akrabalık tiplerini filtreler"""
    if not sulale_data or not isinstance(sulale_data, list):
        return []
    if isinstance(kinship_types, str):
        kinship_types = [kinship_types]
    return [person for person in sulale_data if person.get('YAKINLIK') in kinship_types]

# ============= TEK API ENDPOINT =============

@app.route('/api', methods=['GET'])
def tek_api():
    """
    Tek API endpoint - tüm sorgular buradan yapılır
    """
    type_param = request.args.get('type')
    
    if not type_param:
        return jsonify({
            "error": "type parametresi gerekli",
            "developer": "@ruslonder",
            "available_types": [
                "sulale", "kendisi", "cocuk", "es", "anne", "baba", 
                "kardes", "anneanne", "babanne", "dede", "amca-hala", 
                "dayi-teyze", "kuzen", "tum-akrabalar",
                "adsoyad", "adres", "isyeri", "gsm-tc", "tc-gsm", "tc"
            ]
        }), 400
    
    # ============= SÜLALE AKRABALIK API'LERİ =============
    
    if type_param == "sulale":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/sulale.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "kendisi":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                kendisi = filter_by_kinship(data, "Kendisi")
                return jsonify(kendisi)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "cocuk":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                cocuklar = filter_by_kinship(data, "Çocuğu")
                return jsonify(cocuklar)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "es":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                esler = filter_by_kinship(data, "Eşi")
                return jsonify(esler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "anne":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                anneler = filter_by_kinship(data, "Annesi")
                return jsonify(anneler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "baba":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                babalar = filter_by_kinship(data, "Babası")
                return jsonify(babalar)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "kardes":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                kardesler = filter_by_kinship(data, "Kardeşi")
                return jsonify(kardesler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "anneanne":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                anneanneler = filter_by_kinship(data, "Anneannesi")
                return jsonify(anneanneler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "babanne":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                babaanneler = filter_by_kinship(data, "Babaannesi")
                return jsonify(babaanneler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "dede":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                dedeler = filter_by_kinship(data, ["Dedesi", "Büyükbabası"])
                return jsonify(dedeler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "amca-hala":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                amca_hala = filter_by_kinship(data, "Amca/Hala")
                return jsonify(amca_hala)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "dayi-teyze":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                dayi_teyze = filter_by_kinship(data, "Dayı/Teyze")
                return jsonify(dayi_teyze)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "kuzen":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                kuzenler = filter_by_kinship(data, ["Anne Tarafı Kuzen", "Baba Tarafı Kuzen"])
                return jsonify(kuzenler)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "tum-akrabalar":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            data = fetch_sulale_data(tc)
            if data:
                akrabalar = [kisi for kisi in data if kisi.get('YAKINLIK') != "Kendisi"]
                return jsonify(akrabalar)
            return jsonify([])
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    # ============= TEMEL SORGULAMA API'LERİ =============
    
    elif type_param == "adsoyad":
        adi = request.args.get('adi')
        soyadi = request.args.get('soyadi')
        il = request.args.get('il')
        
        if not adi or not soyadi:
            return jsonify({"error": "adi ve soyadi parametreleri gerekli", "developer": "@ruslonder"}), 400
        try:
            url = f"{BASE_API_URL}/adsoyad.php?adi={adi}&soyadi={soyadi}"
            if il:
                url += f"&il={il}"
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "adres":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/adres.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "isyeri":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/isyeri.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "gsm-tc":
        gsm = request.args.get('gsm')
        if not gsm:
            return jsonify({"error": "gsm parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/gsmtc.php?gsm={gsm}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "tc-gsm":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/tcgsm.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    elif type_param == "tc":
        tc = request.args.get('tc')
        if not tc:
            return jsonify({"error": "tc parametresi gerekli", "developer": "@ruslonder"}), 400
        try:
            response = requests.get(f"{BASE_API_URL}/tc.php?tc={tc}", timeout=10)
            response.encoding = 'utf-8'
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e), "developer": "@ruslonder"}), 500
    
    else:
        return jsonify({
            "error": f"Geçersiz type: {type_param}",
            "developer": "@ruslonder",
            "available_types": [
                "sulale", "kendisi", "cocuk", "es", "anne", "baba", 
                "kardes", "anneanne", "babanne", "dede", "amca-hala", 
                "dayi-teyze", "kuzen", "tum-akrabalar",
                "adsoyad", "adres", "isyeri", "gsm-tc", "tc-gsm", "tc"
            ]
        }), 400

# ============= SAĞLIK KONTROLÜ =============

@app.route('/health', methods=['GET'])
def health():
    """Render için sağlık kontrolü"""
    return jsonify({"status": "healthy", "developer": "@ruslonder"}), 200

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     Akrabalık Sorgulama API v2.0 - Render Uyumlu            ║
    ║         Developer: @ruslonder                                ║
    ║         Tek API: /api?type=...                               ║
    ║         Toplam API Sayısı: 26                                ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Server başlatılıyor...
    Port: """ + str(PORT) + """
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
