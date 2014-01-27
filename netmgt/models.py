from django.db import models
from django.forms import PasswordInput
from ipaddress import IPv4Network

class SwitchPort(models.Model):
    interface = models.CharField(blank=False, null=False, max_length=64)
    switch = models.ForeignKey("Switch")
    network = models.ForeignKey("Network", blank=True, null=True)
    is_uplink = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.interface + " on " + self.switch.hostname

class Switch(models.Model):
    hostname = models.CharField(blank=False, null=False, unique=True, max_length=64)
    uplink_router_interface = models.ForeignKey("RouterPort", blank=True, null=True)
    ip_address = models.IPAddressField(blank=False, null=False, unique=True)
    ssh_username = models.CharField(max_length=64)
    ssh_password = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.hostname

class Router(models.Model):
    hostname = models.CharField(blank=False, null=False, unique=True, max_length=64)
    ip_address = models.IPAddressField(blank=False, null=False, unique=True)
    ssh_username = models.CharField(max_length=64)
    ssh_password = models.CharField(max_length=64)

    def __unicode__(self):
        return self.hostname

class Uplink(models.Model):
    description = models.CharField(blank=True, null=True, unique=True, max_length=255)
    routerport = models.ForeignKey("RouterPort")
    switchport = models.ForeignKey("SwitchPort")
    
    def __unicode__(self):
        return "{routerport} <> {switchport}".format(routerport=self.routerport, switchport=self.switchport)

class RouterPort(models.Model):
    router = models.ForeignKey("Router")
    interface = models.CharField(blank=False, null=False, max_length=64)

    def __unicode__(self):
        return self.interface + " on " + self.router.hostname

class Network(models.Model):
    description = models.CharField(blank=True, null=True, unique=True, max_length=255)
    address = models.IPAddressField(blank=False, null=False, unique=True)
    mask = models.IntegerField(blank=False, null=False)
    netid = models.IntegerField(blank=False, null=False, unique=True)
    configured = models.BooleanField(default=False)
    
    @property
    def netmask(self):
        return str(IPv4Network(unicode("{address}/{mask}".format(address=self.address, mask=self.mask))).netmask)
    @property
    def object(self):
        return IPv4Network(unicode("{address}/{mask}".format(address=self.address, mask=self.mask)))
    
    def __unicode__(self):
        return "({netid}) {address}/{mask} ({description})".format(netid=self.netid, address=self.address, mask=self.mask, description=self.description)