"""
Sodda test sahifasi - Jav    <script>
        function testStart() {
            console.log('=== TEST START FUNCTION CALLED ===');
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '🔄 Test boshlanmoqda...';
            
            console.log('Result div found:', resultDiv);
            console.log('Making fetch request to /api/start/1/');
            
            // CSRF token olish
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            if (csrftoken) {
                headers['X-CSRFToken'] = csrftoken;
            }
            
            fetch('/api/start/1/', {
                method: 'GET',
                headers: headers
            })
                .then(response => {
                    console.log('=== FETCH RESPONSE RECEIVED ===');
                    console.log('Response status:', response.status);
                    console.log('Response ok:', response.ok);
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.status);
                    }
                    return response.json();
                }) uchun
"""
from django.http import HttpResponse
from .models import Question

def simple_test_page(request):
    """Juda sodda test sahifa"""
    questions_count = Question.objects.count()
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Simple Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .btn {{ background: #4CAF50; color: white; padding: 15px 32px; border: none; cursor: pointer; margin: 10px; }}
        #result {{ margin-top: 20px; padding: 15px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>Abitur Test - Sodda Version</h1>
    <p>Mavjud savollar soni: {questions_count}</p>
    
    <button class="btn" onclick="testStart()">🚀 Test Boshlash</button>
    <button class="btn" onclick="testCheck()">✅ Server Tekshirish</button>
    
    <div id="result">Bu yerda natija ko'rsatiladi...</div>
    
    <script>
        function testStart() {{
            console.log('=== TEST START FUNCTION CALLED ===');
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '🔄 Test boshlanmoqda...';
            
            console.log('Result div found:', resultDiv);
            console.log('Making fetch request to /api/start/1/');
            
            fetch('/api/start/1/')
                .then(response => {{
                    console.log('=== FETCH RESPONSE RECEIVED ===');
                    console.log('Response status:', response.status);
                    console.log('Response ok:', response.ok);
                    
                    if (!response.ok) {{
                        throw new Error('Network response was not ok: ' + response.status);
                    }}
                    return response.json();
                }})
                .then(data => {{
                    console.log('=== JSON DATA RECEIVED ===');
                    console.log('API data:', data);
                    resultDiv.innerHTML = '<h3>✅ Test boshland!</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }})
                .catch(error => {{
                    console.error('=== ERROR OCCURRED ===');
                    console.error('Error:', error);
                    resultDiv.innerHTML = '<p style="color: red;">❌ Xatolik: ' + error.message + '</p>';
                }});
        }}
        
        function testCheck() {{
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Server tekshirilmoqda...';
            
            fetch('/api/start/1/')
                .then(response => {{
                    if (response.ok) {{
                        resultDiv.innerHTML = '<p style="color: green;">✅ Server ishlayapti!</p>';
                    }} else {{
                        resultDiv.innerHTML = '<p style="color: red;">❌ Server muammosi: ' + response.status + '</p>';
                    }}
                }})
                .catch(error => {{
                    resultDiv.innerHTML = '<p style="color: red;">❌ Bog\'lanish xatolik: ' + error.message + '</p>';
                }});
        }}
    </script>
</body>
</html>
    """
    return HttpResponse(html)