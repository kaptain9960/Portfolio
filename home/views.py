from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404
from django.http import Http404
from home.models import Blog
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Q
import random
import re

# Create your views here.
def index (request):
    blogs = Blog.objects.all()
    random_blogs = random.sample(list(blogs), 3)
    context = {'random_blogs': random_blogs}
    return render(request, 'index.html', context)

def about (request):
    return render(request, 'about.html')

def thanks(request):
    return render(request, 'thanks.html')

def contact(request):
    if request.method == 'POST':
        # Get form inputs
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Basic empty field check
        if not name or not email or not phone or not message_text:
            messages.error(request, 'One or more fields are empty!')
            return render(request, 'contact.html')

        # Regex patterns
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        phone_pattern = re.compile(r'^[0-9]{11}$')  # Adjust if your phone format differs

        if not email_pattern.match(email):
            messages.error(request, 'Invalid email format!')
            return render(request, 'contact.html')

        if not phone_pattern.match(phone):
            messages.error(request, 'Phone number must be 11 digits!')
            return render(request, 'contact.html')

        # Prepare email content
        email_content = f'''
        From: {name}
        Message: {message_text}
        Email: {email}
        Phone: {phone}
        '''

        try:
            send_mail(
                'You got a mail!',
                email_content,
                settings.EMAIL_HOST_USER,  # Must be your SMTP email
                ['divineigwesi1184@gmail.com'],
                fail_silently=False
            )
            messages.success(request, 'Your message was sent successfully!')
            return redirect('contact')  # Prevent resubmission on refresh
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')

    return render(request, 'contact.html')

def projects (request):
    return render(request, 'projects.html')

def blog(request):
    blogs = Blog.objects.all().order_by('-time')
    paginator = Paginator(blogs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context = {'blogs': blogs}
    return render(request, 'blog.html', context)

def category(request, category):
    category_posts = Blog.objects.filter(category=category).order_by('-time')
    if not category_posts:
        message = f"No posts found in category: '{category}'"
        return render(request, "category.html", {"message": message})
    paginator = Paginator(category_posts, 3)
    page = request.GET.get('page')
    category_posts = paginator.get_page(page)
    return render(request, "category.html", {"category": category, 'category_posts': category_posts})

def categories(request):
    all_categories = Blog.objects.values('category').distinct().order_by('category')
    return render(request, "categories.html", {'all_categories': all_categories})

def search(request):
    query = request.GET.get('q')
    query_list = query.split()
    results = Blog.objects.none()
    for word in query_list:
        results = results | Blog.objects.filter(Q(title__contains=word) | Q(content__contains=word)).order_by('-time')
    paginator = Paginator(results, 3)
    page = request.GET.get('page')
    results = paginator.get_page(page)
    if len(results) == 0:
        message = "Sorry, no results found for your search query."
    else:
        message = ""
    return render(request, 'search.html', {'results': results, 'query': query, 'message': message})


def blogpost (request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        context = {'blog': blog}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)

# def blogpost (request, slug):
#     blog = Blog.objects.filter(slug=slug).first()
#     context = {'blog': blog}
#     return render(request, 'blogpost.html', context)
