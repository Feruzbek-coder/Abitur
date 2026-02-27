"""
Abitur Test API ni sinash uchun Python script
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_start_api():
    """Test boshlash API ni sinaydi"""
    print("🚀 Test boshlash API ni sinamoqda...")
    
    try:
        response = requests.get(f"{BASE_URL}/start/1/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Test muvaffaqiyatli boshlandi!")
            print(f"📝 Test ID: {data.get('attempt_id')}")
            print(f"❓ Savol: {data.get('text')}")
            print("📋 Variantlar:")
            options = data.get('options', {})
            for key, value in options.items():
                print(f"   {key}) {value}")
            return data
        else:
            print(f"❌ Xatolik: {response.status_code}")
            print(f"📄 Javob: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Server bilan bog'lanib bo'lmadi!")
        print("💡 Server ishlaganini tekshiring: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ Kutilmagan xatolik: {e}")
        return None

def test_submit_api(attempt_id, question_id, chosen_answer="A"):
    """Javob yuborish API ni sinaydi"""
    print(f"\n📤 Javob yubormoqda: {chosen_answer}")
    
    try:
        payload = {
            "attempt_id": attempt_id,
            "question_id": question_id,
            "chosen": chosen_answer,
            "time_taken": 5.5
        }
        
        response = requests.post(f"{BASE_URL}/submit/", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Javob muvaffaqiyatli yuborildi!")
            
            if 'finished' in data:
                print("🏁 Test yakunlandi!")
                print(f"🎯 Yakuniy ball: {data.get('score')}")
            else:
                print("➡️ Keyingi savol:")
                print(f"❓ {data.get('text')}")
                print("📋 Variantlar:")
                options = data.get('options', {})
                for key, value in options.items():
                    print(f"   {key}) {value}")
            return data
        else:
            print(f"❌ Xatolik: {response.status_code}")
            print(f"📄 Javob: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Kutilmagan xatolik: {e}")
        return None

def full_test_demo():
    """To'liq test simulatsiyasi"""
    print("🎓 ABITUR TEST SIMULATSIYASI")
    print("=" * 50)
    
    # Test boshlash
    test_data = test_start_api()
    if not test_data:
        return
    
    attempt_id = test_data.get('attempt_id')
    question_id = test_data.get('question_id')
    
    if not attempt_id or not question_id:
        print("❌ Test ma'lumotlari to'liq emas")
        return
    
    # Bir necha javob yuborish (demo uchun)
    answers = ['A', 'B', 'A', 'C', 'A']  # Test javoblar
    
    for i, answer in enumerate(answers):
        print(f"\n🔄 Savol {i+1}: {answer} javobini tanlayapmiz...")
        result = test_submit_api(attempt_id, question_id, answer)
        
        if not result:
            break
            
        if 'finished' in result:
            print(f"\n🎉 Test yakunlandi! Ball: {result.get('score')}")
            break
            
        # Keyingi savolga o'tish
        question_id = result.get('question_id')
        if not question_id:
            print("❌ Keyingi savol topilmadi")
            break

if __name__ == "__main__":
    print("ABITUR TEST API - SINOV DASTURI")
    print("=" * 40)
    print("1. Avval server ishlaganini tekshiring:")
    print("   cd C:\\Abitur\\abitur_test")
    print("   C:/Abitur/.venv/Scripts/python.exe manage.py runserver")
    print("\n2. Keyin ushbu skriptni ishga tushiring")
    print("=" * 40)
    
    input("\\nDavom etish uchun Enter ni bosing...")
    full_test_demo()