from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, NewsCategory


def news_list_view(request):
    """Yangiliklar ro'yxati"""
    category_slug = request.GET.get('category')
    
    # Faqat nashr qilingan yangiliklar
    news_list = News.objects.filter(is_published=True).select_related('category', 'author')
    
    # Kategoriya bo'yicha filtrlash
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
        news_list = news_list.filter(category=selected_category)
    
    # Asosiy yangilik
    featured_news = news_list.filter(is_featured=True).first()
    
    # Paginatsiya
    paginator = Paginator(news_list, 9)  # 9 ta yangilik har sahifada
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    
    # Kategoriyalar
    categories = NewsCategory.objects.filter(is_active=True)
    
    context = {
        'news': news,
        'featured_news': featured_news,
        'categories': categories,
        'selected_category': selected_category,
        'title': 'Yangiliklar'
    }
    return render(request, 'exams/news_list.html', context)


def news_detail_view(request, slug):
    """Yangilik tafsilotlari"""
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    # Ko'rishlar sonini oshirish
    news.increment_views()
    
    # O'xshash yangiliklar
    related_news = News.objects.filter(
        is_published=True,
        category=news.category
    ).exclude(id=news.id).select_related('category', 'author')[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
        'title': news.title
    }
    return render(request, 'exams/news_detail.html', context)
