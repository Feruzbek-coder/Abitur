"""
9-14 yoshli o'quvchilar uchun namuna ma'lumotlar yaratish:
- Qiziqish kategoriyalari va savollari
- Mantiqiy mashqlar va savollar

Ishlatish: python manage.py seed_edukids_kids_sections
"""
import json
from django.core.management.base import BaseCommand
from edukids.models import (
    InterestCategory, InterestQuestion,
    LogicExercise, LogicQuestion
)


class Command(BaseCommand):
    help = "9-14 yoshli o'quvchilar uchun qiziqishlar va mantiqiy mashqlar namunalarini yaratadi"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== EduKids bolalar bo'limlari namunalari ==="))
        self._create_interest_data()
        self._create_logic_data()
        self.stdout.write(self.style.SUCCESS("✅ Barcha namuna ma'lumotlar muvaffaqiyatli yaratildi!"))

    # ──────────── QIZIQISHLAR ────────────
    def _create_interest_data(self):
        self.stdout.write("📌 Qiziqish kategoriyalari yaratilmoqda...")

        categories = [
            {
                "name": "Fan va Texnologiya",
                "description": "Ilm-fan, robotlar, ixtirolar va texnologiyaga qiziqasanmi?",
                "icon": "🔬",
                "color": "#4facfe",
                "careers": ["Dasturchi", "Muhandis", "Olim", "Robotexnik", "Matematik"],
            },
            {
                "name": "San'at va Ijodiyot",
                "description": "Rasm chizish, musiqa, dizayn yoki yozishni yaxshi ko'rasanmi?",
                "icon": "🎨",
                "color": "#f093fb",
                "careers": ["Dizayner", "Rassom", "Musiqachi", "Yozuvchi", "Arxitektor"],
            },
            {
                "name": "Sport va Harakat",
                "description": "Jismoniy faollik, musobaqa va jamoa o'yinlari senga yoqadimi?",
                "icon": "⚽",
                "color": "#11998e",
                "careers": ["Sportchi", "Fitnes murabbiy", "Tabib", "Jismoniy tarbiya o'qituvchisi"],
            },
            {
                "name": "Tabiat va Ekologiya",
                "description": "Hayvonlar, o'simliklar, iqlim va tabiatga qiziqasanmi?",
                "icon": "🌿",
                "color": "#38ef7d",
                "careers": ["Biolog", "Ekolog", "Veterinar", "Geograf", "Dehqon-olim"],
            },
            {
                "name": "Odamlar va Jamiyat",
                "description": "Odamlar bilan muloqot, yordam berish va jamoat ishlari senga yoqadimi?",
                "icon": "🤝",
                "color": "#f7971e",
                "careers": ["Shifokor", "Psixolog", "O'qituvchi", "Ijtimoiy xodim", "Siyosatchi"],
            },
            {
                "name": "Biznes va Tadbirkorlik",
                "description": "Pul ishlash, savdo-sotiq va o'z ishingni qurish senga qiziqmi?",
                "icon": "💼",
                "color": "#667eea",
                "careers": ["Tadbirkor", "Menejment", "Iqtisodchi", "Marketing mutaxassisi"],
            },
        ]

        created = 0
        for i, cat_data in enumerate(categories):
            cat, is_new = InterestCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "description": cat_data["description"],
                    "icon": cat_data["icon"],
                    "color": cat_data["color"],
                    "career_suggestions": json.dumps(cat_data["careers"], ensure_ascii=False),
                    "order": i + 1,
                }
            )
            if is_new:
                created += 1
        self.stdout.write(f"  → {created} yangi kategoriya qo'shildi.")

        # Savol shabloni: options ichidagi weights kategoriya nomlari bilan mos keladi
        self.stdout.write("📌 Qiziqish savollari yaratilmoqda...")

        questions = [
            {
                "text": "Vaqtingiz bo'lsa nima bilan shug'ullanishni xohlaysiz?",
                "type": "single",
                "order": 1,
                "options": [
                    {"text": "🔬 Tajriba va ixtirolar qilish", "weights": {"Fan va Texnologiya": 3}},
                    {"text": "🎨 Rasm chizish yoki qo'l ishi", "weights": {"San'at va Ijodiyot": 3}},
                    {"text": "⚽ Sport o'ynash yoki yugurish", "weights": {"Sport va Harakat": 3}},
                    {"text": "🌿 Tabiatda sayr qilish", "weights": {"Tabiat va Ekologiya": 3}},
                    {"text": "🤝 Do'stlar bilan muloqot", "weights": {"Odamlar va Jamiyat": 3}},
                    {"text": "💼 Kichik biznes o'yinlari", "weights": {"Biznes va Tadbirkorlik": 3}},
                ],
            },
            {
                "text": "Maktabda qaysi fan sizga ko'proq yoqadi?",
                "type": "single",
                "order": 2,
                "options": [
                    {"text": "🔢 Matematika va Fizika", "weights": {"Fan va Texnologiya": 3, "Biznes va Tadbirkorlik": 1}},
                    {"text": "🎭 Musiqa yoki Tasviriy san'at", "weights": {"San'at va Ijodiyot": 3}},
                    {"text": "🏃 Jismoniy tarbiya", "weights": {"Sport va Harakat": 3}},
                    {"text": "🌱 Biologiya yoki Geografiya", "weights": {"Tabiat va Ekologiya": 3}},
                    {"text": "📖 Adabiyot yoki Tarix", "weights": {"Odamlar va Jamiyat": 2, "San'at va Ijodiyot": 1}},
                    {"text": "💰 Iqtisod yoki mehnat ta'limi", "weights": {"Biznes va Tadbirkorlik": 3}},
                ],
            },
            {
                "text": "Katta bo'lganda qanday ishni qilishni xohlaysiz?",
                "type": "single",
                "order": 3,
                "options": [
                    {"text": "💻 Kompyuter yoki texnologiya sohasida", "weights": {"Fan va Texnologiya": 3}},
                    {"text": "🖌️ Ijodiy va badiiy sohalarda", "weights": {"San'at va Ijodiyot": 3}},
                    {"text": "🏅 Professional sportchi bo'lishni", "weights": {"Sport va Harakat": 3}},
                    {"text": "🌳 Tabiat va hayvonlar bilan ishlamoqni", "weights": {"Tabiat va Ekologiya": 3}},
                    {"text": "👨‍⚕️ Odamlarga yordam beruvchi kasb", "weights": {"Odamlar va Jamiyat": 3}},
                    {"text": "🏢 O'z kompaniyamni ochishni", "weights": {"Biznes va Tadbirkorlik": 3}},
                ],
            },
            {
                "text": "Film yoki kitob tanlasangiz qaysi janrni afzal ko'rasiz?",
                "type": "single",
                "order": 4,
                "options": [
                    {"text": "🚀 Ilmiy-fantastik", "weights": {"Fan va Texnologiya": 2}},
                    {"text": "🎬 Sarguzasht va drama", "weights": {"San'at va Ijodiyot": 2, "Odamlar va Jamiyat": 1}},
                    {"text": "🏆 Sport haqida", "weights": {"Sport va Harakat": 3}},
                    {"text": "🦁 Tabiat haqidagi hujjatli", "weights": {"Tabiat va Ekologiya": 3}},
                    {"text": "🧑‍🤝‍🧑 Inson munosabatlari haqida", "weights": {"Odamlar va Jamiyat": 3}},
                    {"text": "💰 Bisnes va muvaffaqiyat haqida", "weights": {"Biznes va Tadbirkorlik": 3}},
                ],
            },
            {
                "text": "Robot yoki kompyuter qurishni o'rganish sizga qiziqarlimi?",
                "type": "scale",
                "order": 5,
                "options": [
                    {"weights": {"Fan va Texnologiya": 1}}
                ],
            },
            {
                "text": "Rassomlik yoki musiqa darslariga qatnashishni xohlaysizmi?",
                "type": "scale",
                "order": 6,
                "options": [
                    {"weights": {"San'at va Ijodiyot": 1}}
                ],
            },
            {
                "text": "Sport musobaqalarida qatnashish sizga qiziqarlimi?",
                "type": "scale",
                "order": 7,
                "options": [
                    {"weights": {"Sport va Harakat": 1}}
                ],
            },
            {
                "text": "Hayvonlar va o'simliklarni kuzatish va ularga g'amxo'rlik qilish sizga yoqadimi?",
                "type": "scale",
                "order": 8,
                "options": [
                    {"weights": {"Tabiat va Ekologiya": 1}}
                ],
            },
            {
                "text": "Do'stlaringizga muammo hal qilishda yordam berish sizga zavq beradimi?",
                "type": "scale",
                "order": 9,
                "options": [
                    {"weights": {"Odamlar va Jamiyat": 1}}
                ],
            },
            {
                "text": "O'z pulini topib, kichik savdo qilishni yoqtirgan vaqtingiz bo'lganmi?",
                "type": "scale",
                "order": 10,
                "options": [
                    {"weights": {"Biznes va Tadbirkorlik": 1}}
                ],
            },
        ]

        q_created = 0
        for q_data in questions:
            q, is_new = InterestQuestion.objects.get_or_create(
                question_text=q_data["text"],
                defaults={
                    "question_type": q_data["type"],
                    "options": json.dumps(q_data["options"], ensure_ascii=False),
                    "order": q_data["order"],
                    "is_active": True,
                }
            )
            if is_new:
                q_created += 1
        self.stdout.write(f"  → {q_created} yangi savol qo'shildi.")
        self.stdout.write(self.style.SUCCESS("  ✅ Qiziqishlar bo'limi tayyor!"))

    # ──────────── MANTIQIY MASHQLAR ────────────
    def _create_logic_data(self):
        self.stdout.write("📌 Mantiqiy mashqlar yaratilmoqda...")

        exercises_data = [
            # ---- NAQSH TOPISH (Oson) ----
            {
                "title": "Raqamlar Naqshini Toping",
                "exercise_type": "pattern",
                "difficulty": 1,
                "icon": "🔢",
                "description": "Berilgan ketma-ketlikdagi naqshni topib, keyingi raqamni aniqlang.",
                "questions": [
                    {
                        "text": "2, 4, 6, 8, __ — keyingi raqam nima?",
                        "correct": "10",
                        "options": ["8", "10", "12", "14"],
                        "explanation": "Har safar 2 qo'shiladi: 2+2=4, 4+2=6, ..., 8+2=10.",
                        "hint": "Har bir raqamni oldingi raqamga qiyoslab ko'ring.",
                        "points": 10,
                    },
                    {
                        "text": "1, 3, 5, 7, __ — keyingi raqam?",
                        "correct": "9",
                        "options": ["8", "9", "10", "11"],
                        "explanation": "Toq sonlar ketma-ketligi: +2. 7+2=9.",
                        "hint": "Bu toq sonlar ketma-ketligi.",
                        "points": 10,
                    },
                    {
                        "text": "5, 10, 15, 20, __ — keyingi raqam?",
                        "correct": "25",
                        "options": ["22", "23", "25", "30"],
                        "explanation": "5ga ko'paytirish jadvalı: +5. 20+5=25.",
                        "hint": "5ga bo'linuvchi sonlar.",
                        "points": 10,
                    },
                    {
                        "text": "1, 4, 9, 16, __ — keyingi raqam?",
                        "correct": "25",
                        "options": ["20", "23", "25", "36"],
                        "explanation": "1²=1, 2²=4, 3²=9, 4²=16, 5²=25. Kvadrat sonlar!",
                        "hint": "1, 2, 3, 4, 5 ning kvadratları.",
                        "points": 15,
                    },
                    {
                        "text": "2, 6, 18, 54, __ — keyingi raqam?",
                        "correct": "162",
                        "options": ["108", "162", "200", "216"],
                        "explanation": "Har safar 3ga ko'paytiriladi: 54×3=162.",
                        "hint": "Har raqam oldingisidan necha marta katta?",
                        "points": 15,
                    },
                ],
            },
            # ---- ANALOGIYA (O'rta) ----
            {
                "title": "So'z Analogiyalari",
                "exercise_type": "analogy",
                "difficulty": 2,
                "icon": "🔁",
                "description": "Birinchi juftlikka o'xshash javobni toping.",
                "questions": [
                    {
                        "text": "Qush : Uchmoq = Baliq : ?",
                        "correct": "Suzmoq",
                        "options": ["Yugumoq", "Suzmoq", "Sakramoq", "Uchmoq"],
                        "explanation": "Qush uchadi, baliq suzadi — har ikkalasi o'z harakatlanish usuli.",
                        "hint": "Baliq qanday harakat qiladi?",
                        "points": 10,
                    },
                    {
                        "text": "Kun : Quyosh = Tun : ?",
                        "correct": "Oy",
                        "options": ["Quyosh", "Yulduz", "Oy", "Zulmat"],
                        "explanation": "Kun vaqtida Quyosh, tun vaqtida Oy ko'radi.",
                        "hint": "Tunni yorituvchi nima?",
                        "points": 10,
                    },
                    {
                        "text": "Maktab : Ta'lim = Kasalxona : ?",
                        "correct": "Davolash",
                        "options": ["O'qitish", "Davolash", "Ovqat", "Dam olish"],
                        "explanation": "Maktab ta'lim beradi, kasalxona davolaydi.",
                        "hint": "Kasalxonaning vazifasi nima?",
                        "points": 10,
                    },
                    {
                        "text": "Suv : Chanqoq = Ovqat : ?",
                        "correct": "Och",
                        "options": ["To'q", "Och", "Uyquchan", "Charchagan"],
                        "explanation": "Suv chanqoqni qondiradi, ovqat ochlikni.",
                        "hint": "Ovqat qanday hisni qondiradi?",
                        "points": 10,
                    },
                    {
                        "text": "Kitob : Kutubxona = Rasm : ?",
                        "correct": "Muzey",
                        "options": ["Maktab", "Do'kon", "Muzey", "Bog'cha"],
                        "explanation": "Kitoblar kutubxonada, rasmlar muzeyda saqlanadi.",
                        "hint": "Rasmlar qaerda namoyish etiladi?",
                        "points": 10,
                    },
                ],
            },
            # ---- MATEMATIK MANTIQ (O'rta) ----
            {
                "title": "Matematik Mantiq Masalalari",
                "exercise_type": "math_logic",
                "difficulty": 2,
                "icon": "➕",
                "description": "Matematik mantiq masalalarini yeching. Har bir masala diqqat va fikrlash talab qiladi.",
                "questions": [
                    {
                        "text": "Ahmadning 12 ta olmasi bor. U 4 ta olmasini Bobonga, 3 tasini Camolga berdi. Ahmadda nechta olma qoldi?",
                        "correct": "5",
                        "options": ["3", "5", "7", "9"],
                        "explanation": "12 - 4 - 3 = 5 olma qoldi.",
                        "hint": "Birin-ketin ayiring.",
                        "points": 10,
                    },
                    {
                        "text": "Bir sinifda 30 ta o'quvchi bor. Ularning yarmidan 3 tasi ko'pi qiz. Nechta o'g'il bola bor?",
                        "correct": "12",
                        "options": ["12", "15", "18", "21"],
                        "explanation": "Yarim = 15. Qizlar: 15+3=18. O'g'illar: 30-18=12.",
                        "hint": "Avval qizlar sonini toping.",
                        "points": 15,
                    },
                    {
                        "text": "3 ta mushuk 3 daqiqada 3 ta sichqonni tutadi. 9 ta mushuk 9 daqiqada nechta sichqon tutadi?",
                        "correct": "27",
                        "options": ["9", "18", "27", "81"],
                        "explanation": "1 mushuk 1 daqiqada 1 sichqon tutadi. 9 mushuk × 9 daqiqa = 81. Lekin har bir mushuk 3 daqiqada 3 ta, demak 9 daqiqada 9 ta tutadi. 9×9=81? Yo'q: Har mushuk 1 ta/daqiqa: 9 mushuk × 9 min = 81. Aslida: 1 mushuk 3min = 1 sichqon (3min/1tutish). 9 mushuk 9 min = 9×(9/3) = 9×3 = 27.",
                        "hint": "Bitta mushuk 3 daqiqada nechta tutadi?",
                        "points": 20,
                    },
                    {
                        "text": "Satr: *** | ** | *** | ** | ___ — keyingi naqsh?",
                        "correct": "***",
                        "options": ["*", "**", "***", "****"],
                        "explanation": "Naqsh: 3 yulduz, 2 yulduz, 3 yulduz, 2 yulduz, keyingisi 3 yulduz.",
                        "hint": "Qaysi naqsh takrorlanmoqda?",
                        "points": 10,
                    },
                    {
                        "text": "Agar bugun chorshanba bo'lsa, 10 kundan keyin qaysi kun bo'ladi?",
                        "correct": "Shanba",
                        "options": ["Juma", "Shanba", "Yakshanba", "Dushanba"],
                        "explanation": "10 = 7 + 3. 7 kun = 1 hafta. Chorshanbadan 3 kun keyin = Shanba.",
                        "hint": "7 kunni haftaga bo'ling.",
                        "points": 15,
                    },
                ],
            },
            # ---- XULOSA CHIQARISH (Qiyin) ----
            {
                "title": "Mantiqiy Xulosa",
                "exercise_type": "deduction",
                "difficulty": 3,
                "icon": "🔍",
                "description": "Berilgan ma'lumotlardan to'g'ri xulosa chiqaring. Qiyin darajadagi mantiqiy topshiriqlar!",
                "questions": [
                    {
                        "text": "Barcha mushuklar hayvon. Vaska mushuk. Xulosa: Vaska nima?",
                        "correct": "Hayvon",
                        "options": ["Hayvon", "Hasharot", "Qush", "Baliq"],
                        "explanation": "Deduksiya: Barcha mushuklar hayvon → Vaska mushuk → Vaska hayvon.",
                        "hint": "Katta guruhga kichik guruh kiradi.",
                        "points": 10,
                    },
                    {
                        "text": "Ali Botirdan katta. Botir Camoldan katta. Ulardan eng kichigi kim?",
                        "correct": "Camol",
                        "options": ["Ali", "Botir", "Camol", "Hammasi teng"],
                        "explanation": "Ali > Botir > Camol. Eng kichigi Camol.",
                        "hint": "Qiyoslash zanjirini tuzing.",
                        "points": 15,
                    },
                    {
                        "text": "Bir qutida 5 ta qizil va 3 ta yashil shar bor. Ko'rmay 2 ta shar olish kerak, ikkala shar ham bir xil rangda bo'lishi uchun eng kam nechta shar olish kerak?",
                        "correct": "3",
                        "options": ["2", "3", "4", "5"],
                        "explanation": "Eng yomon holat: birinchi ikki shar turli rangda bo'lishi mumkin. 3-chi shar olishda albatta bir xil rang takrorlanadi.",
                        "hint": "Eng yomon holatni o'ylang.",
                        "points": 20,
                    },
                    {
                        "text": "Bir oilada 3 ta bola bor. Har ikki bolaning yoshi yig'indisi: 10, 12, va 14. Bolalarning yoshi necha?",
                        "correct": "4, 6, 8",
                        "options": ["4, 6, 8", "3, 7, 9", "5, 5, 9", "2, 8, 10"],
                        "explanation": "A+B=10, A+C=12, B+C=14. Yig'indi: 2(A+B+C)=36, jami=18. A=18-14=4, B=18-12=6, C=18-10=8.",
                        "hint": "Uch juftlik yig'indisini qo'shing.",
                        "points": 25,
                    },
                    {
                        "text": "Agar yolg'onchilar har doim yolg'on gapirsa va to'g'riso'zlar har doim haqiqat gapirsa: Aliyev 'Men yolg'onchiman' deydi. Bu mumkinmi?",
                        "correct": "Mumkin emas",
                        "options": ["Mumkin", "Mumkin emas", "Balki", "Ma'lum emas"],
                        "explanation": "Agar to'g'riso'z bo'lsa, 'Men yolg'onchiman' yolg'on bo'ladi. Agar yolg'onchi bo'lsa, haqiqat gapira olmaydi. Bu paradoks — mumkin emas.",
                        "hint": "Ikki holatni alohida tekshiring.",
                        "points": 25,
                    },
                ],
            },
            # ---- KETMA-KETLIK (Oson) ----
            {
                "title": "Shakl Ketma-ketligi",
                "exercise_type": "sequence",
                "difficulty": 1,
                "icon": "📐",
                "description": "Shakllar yoki harflar ketma-ketligida keyingi elementni toping.",
                "questions": [
                    {
                        "text": "A, B, C, D, __ — keyingi harf?",
                        "correct": "E",
                        "options": ["D", "E", "F", "G"],
                        "explanation": "Alifbo tartibida ketma-ket: A, B, C, D, E.",
                        "hint": "Ingliz alifbosi tartibini ko'ring.",
                        "points": 10,
                    },
                    {
                        "text": "Z, Y, X, W, __ — keyingi harf?",
                        "correct": "V",
                        "options": ["U", "V", "W", "T"],
                        "explanation": "Alifbo teskari tartibida: Z, Y, X, W, V.",
                        "hint": "Alifbo oxiridan boshlanmoqda.",
                        "points": 10,
                    },
                    {
                        "text": "Dushanba, Seshanba, Chorshanba, __ — keyingi kun?",
                        "correct": "Payshanba",
                        "options": ["Juma", "Payshanba", "Shanba", "Yakshanba"],
                        "explanation": "Hafta kunlari tartibi.",
                        "hint": "Hafta kunlarini sanang.",
                        "points": 10,
                    },
                    {
                        "text": "Yanvar, Fevral, Mart, __ — keyingi oy?",
                        "correct": "Aprel",
                        "options": ["Aprel", "May", "Iyun", "Iyul"],
                        "explanation": "Oylar tartibi: Yanvar(1), Fevral(2), Mart(3), Aprel(4).",
                        "hint": "Kalendar oylarini sanang.",
                        "points": 10,
                    },
                    {
                        "text": "1, 1, 2, 3, 5, 8, __ — keyingi raqam? (Fibonacci)",
                        "correct": "13",
                        "options": ["10", "11", "13", "15"],
                        "explanation": "Fibonacci: har raqam oldingi ikkitasining yig'indisi. 5+8=13.",
                        "hint": "Oxirgi ikki raqamni qo'shing.",
                        "points": 20,
                    },
                ],
            },
            # ---- FAZOVIY FIKRLASH (O'rta) ----
            {
                "title": "Fazoviy Mantiq",
                "exercise_type": "spatial",
                "difficulty": 2,
                "icon": "🗺️",
                "description": "Yo'nalishlar va fazoviy fikrlash mashqlari.",
                "questions": [
                    {
                        "text": "Ali shimolga 3 qadam, so'ng sharqqa 4 qadam yurdi. U boshlangan nuqtadan qancha masofada?",
                        "correct": "5",
                        "options": ["3", "4", "5", "7"],
                        "explanation": "Pifagor teoremasi: √(3²+4²) = √(9+16) = √25 = 5.",
                        "hint": "To'g'ri burchakli uchburchak hosil bo'ldi.",
                        "points": 20,
                    },
                    {
                        "text": "Siz shimolga qarab tursangiz va o'ng tomonga burylilsangiz, qaysi tomonga qaraysiz?",
                        "correct": "Sharq",
                        "options": ["Shimol", "Janub", "Sharq", "G'arb"],
                        "explanation": "Shimoldan o'ngga = Sharq.",
                        "hint": "Kompas yo'nalishlarini tasavvur qiling.",
                        "points": 10,
                    },
                    {
                        "text": "Kub shaklning nechta qirrasi bor?",
                        "correct": "12",
                        "options": ["6", "8", "12", "16"],
                        "explanation": "Kubning 12 ta qirrasi (rebro) bor: pastki 4, yuqori 4, vertikal 4.",
                        "hint": "Har tomondan sanang.",
                        "points": 10,
                    },
                    {
                        "text": "Agar qog'ozni ikki marta yarlashtirib, bir burchagini kesib tashlas, ochilganda nechta teshik bo'ladi?",
                        "correct": "4",
                        "options": ["1", "2", "4", "8"],
                        "explanation": "Har yarlashtirishda teshiklar 2 marta ko'payadi: 1 kesim × 2 × 2 = 4.",
                        "hint": "Har yalansganda nima ro'y beradi?",
                        "points": 15,
                    },
                    {
                        "text": "5×5 kvadrat katakda diagonallar kesishgan joyda nechta katak bor?",
                        "correct": "1",
                        "options": ["1", "2", "4", "5"],
                        "explanation": "5×5 kvadratning diagonallari faqat bitta markaziy katakda kesishadi.",
                        "hint": "O'rtadagi nuqtani tasavvur qiling.",
                        "points": 15,
                    },
                ],
            },
        ]

        ex_created = 0
        q_created = 0
        for ex_data in exercises_data:
            ex, is_new = LogicExercise.objects.get_or_create(
                title=ex_data["title"],
                defaults={
                    "exercise_type": ex_data["exercise_type"],
                    "difficulty": ex_data["difficulty"],
                    "icon": ex_data["icon"],
                    "description": ex_data["description"],
                    "is_active": True,
                }
            )
            if is_new:
                ex_created += 1

            for i, q_data in enumerate(ex_data["questions"]):
                q, q_new = LogicQuestion.objects.get_or_create(
                    exercise=ex,
                    question_text=q_data["text"],
                    defaults={
                        "correct_answer": q_data["correct"],
                        "options": json.dumps(q_data["options"], ensure_ascii=False),
                        "explanation": q_data.get("explanation", ""),
                        "hint": q_data.get("hint", ""),
                        "points": q_data.get("points", 10),
                        "order": i + 1,
                    }
                )
                if q_new:
                    q_created += 1

        self.stdout.write(f"  → {ex_created} yangi mashq, {q_created} yangi savol qo'shildi.")
        self.stdout.write(self.style.SUCCESS("  ✅ Mantiqiy fikrlash bo'limi tayyor!"))
