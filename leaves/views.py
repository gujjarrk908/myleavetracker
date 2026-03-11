from django.shortcuts import render, redirect, get_object_or_404
from .models import Leave, get_leave_summary, OfficeLogin
from django.contrib import messages
from datetime import datetime

def dashboard(request):
    summary = get_leave_summary()
    return render(request, 'leaves/dashboard.html', {'summary': summary})

def add_leave(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        remarks = request.POST.get('remarks')
        status = request.POST.get('status', 'TAKEN')

        if not start_date_str or not end_date_str:
            messages.error(request, "Please provide both start and end dates.")
            return redirect('add_leave')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date > end_date:
            messages.error(request, "End date cannot be before start date.")
            return render(request, 'leaves/add_leave.html', {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'remarks': remarks,
                'status': status
            })

        try:
            Leave.objects.create(
                start_date=start_date,
                end_date=end_date,
                remarks=remarks,
                status=status
            )
            messages.success(request, "Leave recorded successfully!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_leave')

    return render(request, 'leaves/add_leave.html')

def edit_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        remarks = request.POST.get('remarks')
        status = request.POST.get('status')

        if not start_date_str or not end_date_str:
            messages.error(request, "Please provide both start and end dates.")
            return redirect('edit_leave', pk=pk)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date > end_date:
            messages.error(request, "End date cannot be before start date.")
            return render(request, 'leaves/edit_leave.html', {'leave': leave})

        try:
            leave.start_date = start_date
            leave.end_date = end_date
            leave.remarks = remarks
            leave.status = status
            leave.save()
            messages.success(request, "Leave updated successfully!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('edit_leave', pk=pk)

    return render(request, 'leaves/edit_leave.html', {'leave': leave})

def log_login(request):
    today = datetime.now().date()
    # Default to today if no date is provided
    date_str = request.GET.get('date') or request.POST.get('date')
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = today
    else:
        target_date = today
        
    login_entry = OfficeLogin.objects.filter(date=target_date).first()
    
    if request.method == 'POST':
        login_time_str = request.POST.get('login_time')
        if login_time_str:
            try:
                login_time = datetime.strptime(login_time_str, '%H:%M').time()
                if login_entry:
                    login_entry.login_time = login_time
                    login_entry.save()
                    messages.success(request, f"Login time updated for {target_date}!")
                else:
                    OfficeLogin.objects.create(date=target_date, login_time=login_time)
                    messages.success(request, f"Login time recorded for {target_date}!")
                return redirect('login_history')
            except ValueError:
                messages.error(request, "Invalid time format.")
        else:
            messages.error(request, "Please provide a login time.")
            
    return render(request, 'leaves/log_login.html', {
        'target_date': target_date,
        'login_entry': login_entry,
        'today': today
    })

def login_history(request, year=None, month=None):
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
        
    # Standardize month and year
    current_month_date = datetime(year, month, 1)
    
    # Calculate prev/next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
        
    logins = OfficeLogin.objects.filter(
        date__year=year, 
        date__month=month
    ).order_by('-date')
    
    return render(request, 'leaves/login_history.html', {
        'logins': logins,
        'current_month': current_month_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'year': year,
        'month': month
    })
