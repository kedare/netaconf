from django.contrib import admin
from netmgt.models import *

class SwitchPortInline(admin.StackedInline):
    model = SwitchPort

class RouterPortInline(admin.StackedInline):
    model = RouterPort

class RouterAdmin(admin.ModelAdmin):
    list_display = ("hostname", "ipv4_address")
    
    inlines = [
        RouterPortInline,
    ]

class SwitchAdmin(admin.ModelAdmin):
    list_display = ("hostname", "ipv4_address")
    
    inlines = [
        SwitchPortInline,
    ]

def set_to_configure(model_admin, request, queryset):
    queryset.update(configured=False)

class NetworkAdmin(admin.ModelAdmin):
    list_display = ("netid", "ipv4_address", "ipv4_mask", "ipv6_address", "ipv6_mask", "description", "configured")
    list_filter = ("configured", "ipv4_mask")
    
    inlines = [
        SwitchPortInline,
    ]
    
    actions = [
        set_to_configure
    ]

class SwitchPortAdmin(admin.ModelAdmin):
    list_display = ("interface", "switch", "is_uplink")
    list_filter = ("is_uplink", "switch")

admin.site.register(SwitchPort, SwitchPortAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Router, RouterAdmin)
admin.site.register(RouterPort)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Uplink)