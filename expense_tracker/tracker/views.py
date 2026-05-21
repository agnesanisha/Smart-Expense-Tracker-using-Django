from django.shortcuts import render, redirect
from .models import Expense

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum

# HOME PAGE
def home(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == "POST":

        title = request.POST['title']
        amount = request.POST['amount']
        category = request.POST['category']

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category
        )

        return redirect('/')

    search = request.GET.get('search')

    expenses = Expense.objects.filter(
        user=request.user
    )

    if search:
        expenses = expenses.filter(title__icontains=search)

    expenses = expenses.order_by('-date')

    total = sum(expense.amount for expense in expenses)

    # expense categories summary 
    category_summary = Expense.objects.filter(
        user=request.user
    ).values('category').annotate(total=Sum('amount'))
    
    return render(request, 'home.html', {
        'expenses': expenses,
        'total': total,
        'category_summary': category_summary
    })



# REGISTER
def register_page(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')


        # Check existing username
        if User.objects.filter(username=username).exists():

            return render(request, 'register.html', {
                'error': 'Username already exists'})

        # Check password match
        if password != confirm_password:
            return render(request, 'register.html', {
            'error': 'Passwords do not match'})

        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, 'register.html')


# LOGIN
def login_page(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/')

        else:

            return render(request, 'login.html',{'error':'Invalid Username and Password'})
    
    return render(request, 'login.html')

# LOGOUT
def logout_page(request):

    logout(request)

    return redirect('/login/')


# DELETE EXPENSE
def delete_expense(request, id):

    expense = Expense.objects.get(id=id)

    expense.delete()

    return redirect('/')

# EDIT EXPENSE
def edit_expense(request, id):

    expense = Expense.objects.get(id=id)

    if request.method == "POST":

        expense.title = request.POST['title']
        expense.amount = request.POST['amount']
        expense.category = request.POST['category']

        expense.save()

        return redirect('/')

    return render(request, 'edit.html', {
        'expense': expense
    })

