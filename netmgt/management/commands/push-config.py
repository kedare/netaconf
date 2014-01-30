from django.core.management.base import BaseCommand, CommandError
from netmgt.models import *
from ipaddress import *
from Exscript import Account
from Exscript.protocols import SSH2
from Exscript.protocols.drivers import ios
from termcolor import colored
import Exscript.protocols.Exception
import time


class Command(BaseCommand):
    help = "Push the configuration to network devices"

    def handle(self, *args, **options):
        networks = Network.objects.filter(configured=False)
        for network in networks:
            for switchport in network.switchport_set.all():
                self.stdout.write(colored(">> Configuration of : {network}".format(
                    network=network), "white"))

                # Switch configuration
                self.stdout.write("[{switch}] Connecting...".format(
                    switch=switchport.switch.hostname))
                acc = Account(switchport.switch.ssh_username, switchport.switch.ssh_password)
                conn = SSH2()
                conn.set_timeout(3)
                conn.set_driver("ios")
                conn.connect(switchport.switch.ipv4_address)
                conn.login(acc)
                self.stdout.write(colored("[{switch}] Connected".format(
                    switch=switchport.switch.hostname), "green"))
                self.stdout.write("[{switch}] Configuring {switchport} as access port".format(
                    switchport=switchport, switch=switchport.switch))
                conn.execute("enable")
                conn.execute("configure terminal")
                conn.execute("vlan {netid}".format(
                    netid=network.netid))
                conn.execute("name VLAN{description}".format(
                    description=network.netid))
                conn.execute("default interface {iface}".format(
                    iface=switchport.interface))
                conn.execute("interface {iface}".format(
                    iface=switchport.interface))
                conn.execute("spanning-tree portfast")
                conn.execute("description {description}".format(
                    description=network.description))
                conn.execute("switchport mode access")
                conn.execute("switchport access vlan {netid}".format(
                    netid=network.netid))
                conn.execute("no shutdown")
                conn.execute("end")

                uplink = switchport.switch.switchport_set.filter(
                    is_uplink=True).first()

                try:
                    conn.execute("exit")
                    conn.close()
                except:
                    pass
                del conn
                self.stdout.write(colored("[{switch}] Configuration complete for {switchport}".format(
                    switch=switchport.switch.hostname, switchport=switchport), "green"))

                # Router configuration
                router_success = False
                while not router_success:
                    try:
                        routerport = uplink.uplink_set.first().routerport
                        router = routerport.router
                        self.stdout.write("[{router}] Connecting".format(
                            router=router.hostname))
                        acc = Account(router.ssh_username, router.ssh_password)
                        conn = SSH2()
                        conn.set_timeout(3)
                        conn.set_driver("ios")
                        conn.connect(router.ipv4_address)
                        conn.login(acc)
                        iface = "{routerport}.{netid}".format(
                            routerport=routerport.interface, netid=network.netid)
                        self.stdout.write(colored("[{router}] Connected".format(
                            router=router.hostname), "green"))
                        self.stdout.write("[{router}] Defaulting interface {iface}".format(
                            router=router.hostname, iface=iface))
                        conn.execute("enable")
                        conn.execute("configure terminal")
                        conn.execute("interface {iface}".format(iface=iface))
                        conn.execute("no interface {iface}".format(iface=iface))
                        self.stdout.write("[{router}] Configuring interface {iface}".format(
                            router=router.hostname, iface=iface))
                        conn.execute("interface {iface}".format(iface=iface))
                        conn.execute("encapsulation dot1Q {netid}".format(netid=network.netid))
                        conn.execute("ip address {address4} {netmask4}".format(
                            address4=str(network.object4.hosts().next()), netmask4=network.netmask4))
                        conn.execute("ipv6 enable")
                        conn.execute("ipv6 address {address6}/{netmask6}".format(
                            address6=str(network.object6.hosts().next()), netmask6=network.ipv6_mask))
                        conn.execute("ipv6 nd prefix {address6}/{netmask6}".format(
                            address6=str(network.ipv6_address), netmask6=network.ipv6_mask))
                        conn.execute("no shutdown")
                        conn.execute("ip nat inside")
                        conn.execute("end")
                        self.stdout.write("[{router}] Configuring DHCPv4 Pool".format(
                            router=router.hostname))
                        conn.execute("configure terminal")
                        conn.execute("ip dhcp pool DHCP-{netid}".format(
                            netid=network.netid))
                        conn.execute("network {address4} {netmask4}".format(
                            address4=network.ipv4_address, netmask4=network.netmask4))
                        conn.execute("default-router {address4}".format(
                            address4=str(network.object4.hosts().next())))
                        conn.execute("dns-server {address4}".format(
                            address4=str(network.object4.hosts().next())))
                        conn.execute("end")
                        router_success = True
                        network.configured = True
                        network.save()
                        try:
                            conn.execute("exit")
                            conn.close()
                        except:
                            pass

                        del conn
                        self.stdout.write(colored("[{router}] Configuration complete for VLAN {netid}".format(
                            router=router.hostname, netid=network.netid), "green"))
                    except Exscript.protocols.Exception.TimeoutException:
                        self.stdout.write(colored("[{router}] Connection failed".format(
                            router=router.hostname), "red"))
                        time.sleep(3)

                self.stdout.write("")
