from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Service, StatusCheck, OutagePeriod

@api_view(['GET'])
def status_overview(request):
    services_data = []
    
    # Use UTC timezone
    utc_now = timezone.now()
    
    for service in Service.objects.filter(is_active=True):
        # Get today's start in UTC
        today_start = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's checks
        today_checks = StatusCheck.objects.filter(
            service=service,
            checked_at__gte=today_start
        ).order_by('checked_at')
        
        # Get latest check (current status)
        latest_check = StatusCheck.objects.filter(service=service).order_by('-checked_at').first()
        
        # Calculate uptime for today
        today_operational = today_checks.filter(status='operational').count()
        today_total = today_checks.count()
        uptime_today = (today_operational / today_total * 100) if today_total > 0 else 100
        
        # Format today's history for the status bar (UTC time)
        today_history = []
        for check in today_checks:
            today_history.append({
                'time': check.checked_at.strftime('%H:%M'),
                'status': check.status,
                'response_time': check.response_time,
                'full_time': check.checked_at.isoformat()
            })
        
        # Get detailed outage timeline for last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        outages = OutagePeriod.objects.filter(
            service=service,
            started_at__gte=seven_days_ago
        ).order_by('-started_at')
        
        # Create detailed timeline for last 7 days
        detailed_timeline = []
        for day in range(7):
            day_date = (utc_now - timedelta(days=day)).date()
            day_start = timezone.make_aware(datetime.combine(day_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(day_date, datetime.max.time()))
            
            # Get all outages for this day
            day_outages = outages.filter(
                started_at__date=day_date
            )
            
            # Calculate operational periods
            if day_outages.exists():
                status = 'mixed'
                outage_details = []
                for outage in day_outages:
                    if outage.resolved_at:
                        duration = outage.duration_minutes
                        outage_details.append({
                            'start_time': outage.started_at.strftime('%H:%M'),
                            'end_time': outage.resolved_at.strftime('%H:%M'),
                            'duration': f"{duration}min",
                            'status': 'outage'
                        })
                    else:
                        outage_details.append({
                            'start_time': outage.started_at.strftime('%H:%M'),
                            'end_time': 'Ongoing',
                            'duration': 'Ongoing',
                            'status': 'outage'
                        })
            else:
                status = 'operational'
                outage_details = []
                
            detailed_timeline.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'day_name': day_date.strftime('%A'),
                'status': status,
                'outage_count': len(day_outages),
                'outage_details': outage_details,
                'is_today': day_date == utc_now.date()
            })
        
        # Format last checked time in UTC
        if latest_check:
            last_checked = latest_check.checked_at.isoformat()
            last_checked_display = latest_check.checked_at.strftime('%H:%M UTC')
        else:
            last_checked = None
            last_checked_display = None
        
        services_data.append({
            'name': service.name,
            'description': service.description,
            'url': service.url,
            'current_status': latest_check.status if latest_check else 'unknown',
            'response_time': latest_check.response_time if latest_check else 0,
            'uptime_today': round(uptime_today, 1),
            'today_history': today_history,
            'last_7_days_timeline': detailed_timeline[::-1],  # Oldest first
            'last_checked': last_checked,
            'last_checked_display': last_checked_display,
            'timezone': 'UTC'
        })
    
    return Response({
        'services': services_data,
        'last_updated': utc_now.isoformat(),
        'last_updated_display': utc_now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'timezone': 'UTC'
    })