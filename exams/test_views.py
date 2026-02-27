from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Question, UserProfile

@login_required
def test_page(request):
    """Test uchun HTML sahifa - foydalanuvchi yo'nalishi bo'yicha"""
    
    # Profil va yo'nalish tekshirish
    try:
        profile = request.user.profile
        if not profile.selected_subject:
            messages.warning(request, 'Iltimos, avval yo\'nalishni tanlang.')
            return redirect('exams:profile_setup')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil topilmadi.')
        return redirect('exams:profile_setup')
    
    # Tanlangan yo'nalish bo'yicha savollar soni
    questions_count = Question.objects.filter(subject=profile.selected_subject).count()
    
    if questions_count == 0:
        messages.error(request, f'{profile.selected_subject.display_name} yo\'nalishi bo\'yicha savollar mavjud emas.')
        return redirect('exams:dashboard')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="csrf-token" content="{{{{ csrf_token }}}}">
        <title>Abituriyent Test - {profile.selected_subject.display_name}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .test-container {{ 
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin: 2rem auto;
                overflow: hidden;
            }}
            .question-card {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                transition: all 0.3s ease;
            }}
            .question-card:hover {{
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .option {{
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 12px 15px;
                margin: 8px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .option:hover {{
                background: #e3f2fd;
                border-color: #2196f3;
                transform: translateX(5px);
            }}
            .option.selected {{
                background: #4caf50;
                color: white;
                border-color: #45a049;
            }}
            .test-progress {{
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
            }}
            .progress-bar {{
                height: 100%;
                background: linear-gradient(45deg, #4caf50, #45a049);
                transition: width 0.3s ease;
            }}
            .timer {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #dc3545;
            }}
            .btn-custom {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .btn-custom:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row justify-content-center">
                <div class="col-lg-8 col-xl-6">
                    <div class="test-container">
                        <div class="card-header bg-primary text-white text-center p-4">
                            <h2><i class="fas fa-graduation-cap me-2"></i>Abituriyent Test</h2>
                            <p class="mb-2"><strong>{profile.selected_subject.display_name}</strong> yo'nalishi</p>
                            <p class="mb-0 small">Jami savollar: {questions_count} ta</p>
                        </div>
                        <div class="card-body p-4">
                            <!-- Test boshlanishidan oldin -->
                            <div id="start-section">
                                <div class="text-center mb-4">
                                    <i class="fas fa-clock text-primary mb-3" style="font-size: 3rem;"></i>
                                    <h4>Test haqida ma'lumot</h4>
                                    <div class="row text-center mt-4">
                                        <div class="col-4">
                                            <i class="fas fa-questions-circle text-info"></i>
                                            <p class="mb-0"><strong>{questions_count}</strong></p>
                                            <small class="text-muted">Savollar</small>
                                        </div>
                                        <div class="col-4">
                                            <i class="fas fa-clock text-warning"></i>
                                            <p class="mb-0"><strong>120</strong></p>
                                            <small class="text-muted">Daqiqa</small>
                                        </div>
                                        <div class="col-4">
                                            <i class="fas fa-trophy text-success"></i>
                                            <p class="mb-0"><strong>60%</strong></p>
                                            <small class="text-muted">O'tish ball</small>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    <strong>Muhim:</strong> Test boshlangandan so'ng vaqt hisoblanishni boshlaydi. 
                                    Har bir savol uchun 4 ta variant berilgan, to'g'ri javobni tanlang.
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button onclick="startTest()" class="btn btn-custom btn-lg">
                                        <i class="fas fa-play me-2"></i>Testni Boshlash
                                    </button>
                                    <a href="/dashboard/" class="btn btn-outline-secondary">
                                        <i class="fas fa-arrow-left me-2"></i>Bosh sahifaga qaytish
                                    </a>
                                </div>
                            </div>
                            
                            <!-- Test davomida -->
                            <div id="test-section" style="display: none;">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <div class="timer">
                                        <i class="fas fa-clock me-2"></i>
                                        <span id="timer">120:00</span>
                                    </div>
                                    <div class="text-muted">
                                        <span id="current-question">1</span> / <span id="total-questions">{questions_count}</span>
                                    </div>
                                </div>
                                
                                <div class="test-progress mb-4">
                                    <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
                                </div>
                                
                                <div id="question-container" class="question-card p-4 mb-4">
                                    <!-- Savol shu yerda ko'rsatiladi -->
                                </div>
                                
                                <div class="d-flex justify-content-between">
                                    <button id="prev-btn" onclick="previousQuestion()" class="btn btn-outline-secondary" disabled>
                                        <i class="fas fa-chevron-left me-2"></i>Oldingi
                                    </button>
                                    <button id="next-btn" onclick="nextQuestion()" class="btn btn-custom">
                                        Keyingi<i class="fas fa-chevron-right ms-2"></i>
                                    </button>
                                    <button id="finish-btn" onclick="finishTest()" class="btn btn-success" style="display: none;">
                                        <i class="fas fa-check me-2"></i>Testni Yakunlash
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Test yakunlangandan keyin -->
                            <div id="result-section" style="display: none;">
                                <div class="text-center">
                                    <i class="fas fa-chart-bar text-success mb-3" style="font-size: 3rem;"></i>
                                    <h4>Test yakunlandi!</h4>
                                    <div id="test-results" class="mt-4">
                                        <!-- Natijalar shu yerda ko'rsatiladi -->
                                    </div>
                                    <div class="mt-4">
                                        <a href="/dashboard/" class="btn btn-primary">
                                            <i class="fas fa-home me-2"></i>Bosh sahifa
                                        </a>
                                        <button onclick="restartTest()" class="btn btn-outline-secondary ms-2">
                                            <i class="fas fa-redo me-2"></i>Qayta boshlash
                                        </button>
                                    </div>
                                </div>
                            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentTest = null;
            let selectedAnswer = null;
            let currentQuestionIndex = 0;
            let timer = null;
            let timeLeft = 120 * 60; // 120 daqiqa
            let userAnswers = [];
            
            // Test boshlash
            async function startTest() {{
                document.getElementById('start-section').style.display = 'none';
                document.getElementById('test-section').style.display = 'block';
                
                startTimer();
                await loadNextQuestion();
            }}
            
            // Vaqt hisoblagich
            function startTimer() {{
                timer = setInterval(() => {{
                    timeLeft--;
                    updateTimer();
                    
                    if (timeLeft <= 0) {{
                        clearInterval(timer);
                        finishTest();
                    }}
                }}, 1000);
            }}
            
            function updateTimer() {{
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                document.getElementById('timer').textContent = 
                    `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            }}
            
            // Keyingi savolni yuklash
            async function loadNextQuestion() {{
                try {{
                    const response = await fetch('/api/start/1/', {{
                        headers: {{
                            'X-CSRFToken': getCookie('csrftoken')
                        }}
                    }});
                    if (response.ok) {{
                        const data = await response.json();
                        currentTest = data;
                        displayQuestion(data);
                        updateProgress();
                    }} else {{
                        console.error('API xatolik:', response.status);
                        alert('Savol yuklashda xatolik yuz berdi!');
                    }}
                }} catch (error) {{
                    console.error('Savol yuklashda xatolik:', error);
                    alert('Tarmoq xatoligi!');
                }}
            }}
            
            // Savolni ko'rsatish
            function displayQuestion(data) {{
                const container = document.getElementById('question-container');
                let optionsHtml = '';
                
                Object.entries(data.options).forEach(([key, value]) => {{
                    optionsHtml += `
                        <div class="option" onclick="selectAnswer('${{key}}', this)">
                            <strong>${{key}})</strong> ${{value}}
                        </div>
                    `;
                }});
                
                container.innerHTML = `
                    <h5 class="mb-4">${{data.text}}</h5>
                    <div class="options">
                        ${{optionsHtml}}
                    </div>
                `;
                
                selectedAnswer = null;
                document.getElementById('next-btn').disabled = true;
            }}
            
            // Javobni tanlash
            function selectAnswer(answer, element) {{
                // Oldingi tanlovni o'chirish
                document.querySelectorAll('.option').forEach(opt => {{
                    opt.classList.remove('selected');
                }});
                
                // Yangi tanlovni belgilash
                element.classList.add('selected');
                selectedAnswer = answer;
                
                // Keyingi tugmasini yoqish
                document.getElementById('next-btn').disabled = false;
            }}
            
            // Keyingi savol
            async function nextQuestion() {{
                if (!selectedAnswer) {{
                    alert('Iltimos, javobni tanlang!');
                    return;
                }}
                
                // Javobni yuborish
                await submitAnswer();
                
                currentQuestionIndex++;
                updateProgress();
                
                // Oxirgi savolmi tekshirish
                const totalQuestions = parseInt(document.getElementById('total-questions').textContent);
                if (currentQuestionIndex >= totalQuestions - 1) {{
                    document.getElementById('next-btn').style.display = 'none';
                    document.getElementById('finish-btn').style.display = 'block';
                }} else {{
                    await loadNextQuestion();
                }}
            }}
            
            // Oldingi savol
            function previousQuestion() {{
                if (currentQuestionIndex > 0) {{
                    currentQuestionIndex--;
                    updateProgress();
                    // Oldingi savol ma'lumotlarini qaytarish logikasi
                }}
            }}
            
            // Progress yangilash
            function updateProgress() {{
                const totalQuestions = parseInt(document.getElementById('total-questions').textContent);
                const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
                document.getElementById('progress-bar').style.width = progress + '%';
                document.getElementById('current-question').textContent = currentQuestionIndex + 1;
                
                // Oldingi tugmasini boshqarish
                document.getElementById('prev-btn').disabled = currentQuestionIndex === 0;
            }}
            
            // Javobni yuborish
            async function submitAnswer() {{
                if (!currentTest || !selectedAnswer) return;
                
                try {{
                    const response = await fetch('/api/submit/', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }},
                        body: JSON.stringify({{
                            attempt_id: currentTest.attempt_id,
                            question_id: currentTest.question_id,
                            chosen: selectedAnswer,
                            time_taken: 10
                        }})
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        userAnswers.push({{
                            question: currentTest.text,
                            user_answer: selectedAnswer,
                            correct: result.is_correct || false,
                            correct_answer: result.correct_answer
                        }});
                    }}
                }} catch (error) {{
                    console.error('Javob yuborishda xatolik:', error);
                }}
            }}
            
            // Testni yakunlash
            function finishTest() {{
                clearInterval(timer);
                document.getElementById('test-section').style.display = 'none';
                document.getElementById('result-section').style.display = 'block';
                
                showResults();
            }}
            
            // Natijalarni ko'rsatish
            function showResults() {{
                const resultsContainer = document.getElementById('test-results');
                const correctAnswers = userAnswers.filter(a => a.correct).length;
                const totalQuestions = userAnswers.length;
                const percentage = Math.round((correctAnswers / totalQuestions) * 100);
                
                const isPassed = percentage >= 60;
                const statusClass = isPassed ? 'success' : 'danger';
                const statusIcon = isPassed ? 'fa-check-circle' : 'fa-times-circle';
                const statusText = isPassed ? 'O\\'tdingiz!' : 'O\\'tmadingiz!';
                
                resultsContainer.innerHTML = `
                    <div class="alert alert-${{statusClass}} text-center">
                        <i class="fas ${{statusIcon}} fa-2x mb-2"></i>
                        <h4>${{statusText}}</h4>
                        <p class="mb-0">Natija: <strong>${{correctAnswers}}/${{totalQuestions}} (${{percentage}}%)</strong></p>
                    </div>
                    
                    <div class="row text-center mt-4">
                        <div class="col-4">
                            <i class="fas fa-check text-success"></i>
                            <p class="mb-0"><strong>${{correctAnswers}}</strong></p>
                            <small>To'g'ri</small>
                        </div>
                        <div class="col-4">
                            <i class="fas fa-times text-danger"></i>
                            <p class="mb-0"><strong>${{totalQuestions - correctAnswers}}</strong></p>
                            <small>Noto'g'ri</small>
                        </div>
                        <div class="col-4">
                            <i class="fas fa-percentage text-info"></i>
                            <p class="mb-0"><strong>${{percentage}}%</strong></p>
                            <small>Ball</small>
                        </div>
                    </div>
                `;
            }}
            
            // Qayta boshlash
            function restartTest() {{
                currentQuestionIndex = 0;
                timeLeft = 120 * 60;
                userAnswers = [];
                selectedAnswer = null;
                
                document.getElementById('result-section').style.display = 'none';
                document.getElementById('start-section').style.display = 'block';
                document.getElementById('next-btn').style.display = 'block';
                document.getElementById('finish-btn').style.display = 'none';
            }}
            
            // CSRF token olish
            function getCookie(name) {{
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {{
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {{
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }}
                    }}
                }}
                // Meta tagdan ham olishga harakat qilamiz
                if (!cookieValue) {{
                    const metaToken = document.querySelector('meta[name="csrf-token"]');
                    if (metaToken) {{
                        cookieValue = metaToken.getAttribute('content');
                    }}
                }}
                return cookieValue;
            }}
        </script>
    </body>
    </html>
    """
    
    
    # Template uchun context yaratamiz
    context = {
        'profile': profile,
        'questions_count': questions_count,
    }
    
    # Template stringni render qilamiz 
    from django.template import Template, Context
    from django.template.context_processors import csrf
    template = Template(html_content)
    
    # CSRF tokenni qo'shamiz
    context.update(csrf(request))
    
    return HttpResponse(template.render(Context(context)))

def questions_list(request):
    """Savollar ro'yxatini JSON da qaytaradi"""
    questions = Question.objects.all().values('id', 'text', 'level')
    return JsonResponse(list(questions), safe=False)