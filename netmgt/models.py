from django.db import models
from django.forms import PasswordInput
from ipaddress import IPv4Network, IPv6Network


class SwitchPort(models.Model):
    interface = models.CharField(blank=False, null=False, max_length=64)
    switch = models.ForeignKey("Switch")
    network = models.ForeignKey("Network", blank=True, null=True)
    is_uplink = models.BooleanField(default=False)

    def __unicode__(self):
        return self.interface + " on " + self.switch.hostname


class Switch(models.Model):
    hostname = models.CharField(blank=False, null=False,
                                unique=True, max_length=64)
    uplink_router_interface = models.ForeignKey("RouterPort",
                                                blank=True, null=True)
    ipv4_address = models.IPAddressField(blank=False,
                                         null=False, unique=True)
    ssh_username = models.CharField(max_length=64)
    ssh_password = models.CharField(max_length=64)

    def __unicode__(self):
        return self.hostname


class Router(models.Model):
    hostname = models.CharField(blank=False, null=False,
                                unique=True, max_length=64)
    ipv4_address = models.IPAddressField(blank=False,
                                         null=False, unique=True)
    ssh_username = models.CharField(max_length=64)
    ssh_password = models.CharField(max_length=64)

    def __unicode__(self):
        return self.hostname


class Uplink(models.Model):
    description = models.CharField(blank=True, null=True,
                                   unique=True, max_length=255)
    routerport = models.ForeignKey("RouterPort")
    switchport = models.ForeignKey("SwitchPort")

    def __unicode__(self):
        return "{routerport} <> {switchport}".format(
            routerport=self.routerport,
            switchport=self.switchport)


class RouterPort(models.Model):
    router = models.ForeignKey("Router")
    interface = models.CharField(blank=False, null=False, max_length=64)

    def __unicode__(self):
        return self.interface + " on " + self.router.hostname


class Network(models.Model):
    description = models.CharField(blank=True, null=True,
                                   unique=True, max_length=255)
    ipv4_address = models.GenericIPAddressField(blank=False, null=False,
                                                unique=True, protocol="IPv4")
    ipv4_mask = models.IntegerField(blank=False, null=False)
    ipv6_address = models.GenericIPAddressField(blank=False, null=False,
                                                unique=True, protocol="IPv6")
    ipv6_mask = models.IntegerField(blank=False, null=False)
    netid = models.IntegerField(blank=False, null=False,
                                unique=True)
    configured = models.BooleanField(default=False)

    @property
    def object4(self):
        return IPv4Network(unicode("{address}/{mask}".format(
            address=self.ipv4_address, mask=self.ipv4_mask)))

    @property
    def netmask4(self):
        return str(self.object4.netmask)

    @property
    def object6(self):
        return IPv6Network(unicode("{address}/{mask}".format(
            address=self.ipv6_address, mask=self.ipv6_mask)))

    @property
    def netmask6(self):
        return str(self.object6.netmask)

    def __unicode__(self):
        return "({netid}) ({description})".format(
            netid=self.netid, address4=self.ipv4_address, mask4=self.ipv4_mask,
            address6=self.ipv6_address, mask6=self.ipv6_mask,
            description=self.description)
