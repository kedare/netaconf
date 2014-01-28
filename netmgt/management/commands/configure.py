from django.core.management.base import BaseCommand, CommandError
from netmgt.models import *
from ipaddress import *
from Exscript import Account
from Exscript.protocols import SSH2
from Exscript.protocols.drivers import ios
import Exscript.protocols.Exception

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        networks = Network.objects.filter(configured=False)
        for network in networks:
            for switchport in network.switchport_set.all():
                self.stdout.write(">> CONFIGURATION OF NETWORK : {network}".format(network=network))
                
                # Switch configuration
                self.stdout.write("Connecting to switch...")
                acc = Account(switchport.switch.ssh_username, switchport.switch.ssh_password)
                conn = SSH2()
                conn.set_timeout(3)
                conn.set_driver("ios")
                conn.connect(switchport.switch.ip_address)
                conn.login(acc)
                self.stdout.write("Connected to {switch}".format(switch=switchport.switch.hostname))
                self.stdout.write("Configuring access {switchport} on {switch}".format(switchport=switchport, switch=switchport.switch))
                conn.execute("enable")
                conn.execute("configure terminal")
                conn.execute("vlan {netid}".format(netid=network.netid))
                conn.execute("name VLAN{description}".format(description=network.netid))
                conn.execute("interface {iface}".format(iface=switchport.interface))
                conn.execute("description {description}".format(description=network.description))
                conn.execute("switchport mode access")
                conn.execute("switchport access vlan {netid}".format(netid=network.netid))
                conn.execute("no shutdown")
                conn.execute("end")
                
                uplink = switchport.switch.switchport_set.filter(is_uplink=True).first()
                try:
                    conn.execute("exit")
                    conn.close()
                except:
                    pass
                
                del conn
                self.stdout.write("Switch configuration complete")
                
                # Router configuration
                router_success = False
                while not router_success:
                    try:
                        self.stdout.write("Connecting to router...")
                        routerport = uplink.uplink_set.first().routerport
                        router = routerport.router
                        acc = Account(router.ssh_username, router.ssh_password)
                        conn = SSH2()
                        conn.set_timeout(3)
                        conn.set_driver("ios")
                        conn.connect(router.ip_address)
                        conn.login(acc)
                        print("Connected to {router}".format(router=router.hostname))
                        conn.execute("enable")
                        conn.execute("configure terminal")
                        conn.execute("interface {routerport}.{netid}".format(routerport=routerport.interface, netid=network.netid))
                        conn.execute("encapsulation dot1Q {netid}".format(netid=network.netid))
                        conn.execute("ip address {address} {netmask}".format(address=str(network.object.hosts().next()), netmask=network.netmask))
                        conn.execute("no shutdown")
                        conn.execute("ip nat inside")
                        conn.execute("end")
                        conn.execute("configure terminal")  
                        conn.execute("ip dhcp pool DHCP-{netid}".format(netid=network.netid))
                        conn.execute("network {address} {netmask}".format(address=network.address, netmask=network.netmask))
                        conn.execute("default-router {address}".format(address=str(network.object.hosts().next())))
                        conn.execute("dns-server {address}".format(address=str(network.object.hosts().next())))
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
                        self.stdout.write("Router configuration complete")
                    except Exscript.protocols.Exception.TimeoutException:
                        self.stdout.write("Connection failed")
                    
                self.stdout.write("")