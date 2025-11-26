from django.contrib import admin
from django.utils import timezone
from .models import Service, StatusCheck, OutagePeriod

class UTCTimeAdmin(admin.ModelAdmin):
    def utc_time(self, obj):
        return obj.checked_at.strftime('%b. %d, %Y, %I:%M %p')
    utc_time.short_description = 'Checked at (UTC)'

@admin.register(StatusCheck)
class StatusCheckAdmin(UTCTimeAdmin):
    list_display = ['service', 'status', 'response_time', 'utc_time']
    list_filter = ['status', 'service', 'checked_at']
    readonly_fields = ['checked_at']
    date_hierarchy = 'checked_at'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'url']

@admin.register(OutagePeriod)
class OutagePeriodAdmin(admin.ModelAdmin):
    list_display = ['service', 'started_at_utc', 'resolved_at_utc', 'duration_minutes']
    list_filter = ['service', 'started_at']
    readonly_fields = ['duration_minutes']
    date_hierarchy = 'started_at'
    
    def started_at_utc(self, obj):
        return obj.started_at.strftime('%b. %d, %Y, %I:%M %p')
    started_at_utc.short_description = 'Started at (UTC)'
    
    def resolved_at_utc(self, obj):
        if obj.resolved_at:
            return obj.resolved_at.strftime('%b. %d, %Y, %I:%M %p')
        return '-'
    resolved_at_utc.short_description = 'Resolved at (UTC)'