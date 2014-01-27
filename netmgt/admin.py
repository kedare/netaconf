from django.contrib import admin
from netmgt.models import *

class SwitchPortInline(admin.StackedInline):
    model = SwitchPort

class RouterPortInline(admin.StackedInline):
    model = RouterPort

class RouterAdmin(admin.ModelAdmin):
    list_display = ("hostname", "ip_address")
    
    inlines = [
        RouterPortInline,
    ]

class SwitchAdmin(admin.ModelAdmin):
    list_display = ("hostname", "ip_address")
    
    inlines = [
        SwitchPortInline,
    ]

class NetworkAdmin(admin.ModelAdmin):
    list_display = ("netid", "address", "mask", "description", "configured")
    list_filter = ("configured", "mask")
    
    inlines = [
        SwitchPortInline,
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