from exams.models import Question

# Level 1 test savollari yaratish
questions = [
    {
        'level': 1,
        'text': 'Python dasturlash tilining yaratuvchisi kim?',
        'option_a': 'Guido van Rossum',
        'option_b': 'Dennis Ritchie', 
        'option_c': 'James Gosling',
        'option_d': 'Brendan Eich',
        'correct': 'A'
    },
    {
        'level': 1,
        'text': 'HTML ning to\'liq nomi nima?',
        'option_a': 'Hyper Text Markup Language',
        'option_b': 'High Tech Modern Language',
        'option_c': 'Home Tool Markup Language',
        'option_d': 'Hyperlink and Text Markup Language',
        'correct': 'A'
    },
    {
        'level': 1,
        'text': 'CSS ning asosiy vazifasi nima?',
        'option_a': 'Ma\'lumotlar bazasini boshqarish',
        'option_b': 'Web sahifalarni dizayn qilish',
        'option_c': 'Server mantiqini yozish',
        'option_d': 'Fayllarni arxivlash',
        'correct': 'B'
    },
    {
        'level': 1,
        'text': 'JavaScript dasturlash tili qaysi kompaniya tomonidan yaratilgan?',
        'option_a': 'Microsoft',
        'option_b': 'Google',
        'option_c': 'Netscape',
        'option_d': 'Apple',
        'correct': 'C'
    },
    {
        'level': 1,
        'text': 'HTTP ning to\'liq nomi nima?',
        'option_a': 'HyperText Transfer Protocol',
        'option_b': 'High Technology Transport Protocol',
        'option_c': 'Home Text Transfer Protocol',
        'option_d': 'Hyperlink Text Transport Protocol',
        'correct': 'A'
    }
]

for q_data in questions:
    question = Question.objects.create(**q_data)
    print(f"Yaratildi: {question}")

print(f"Jami {len(questions)} ta savol yaratildi!")
print(f"Hozir bazada {Question.objects.count()} ta savol mavjud.")