from django.core.management.base import BaseCommand, CommandError
from netmgt.models import Network
from ipaddress import IPv4Network, IPv6Network

class Command(BaseCommand):
    args = "<ipv4 supernetwork/mask> <ipv4 subnetmask> <ipv6 supernetwork/mask> (MUST BE INFERIOR TO 64) <ipv6 subnetmask> (MUST BE 64) <firstnetid>"
    help = "Generates all the subnets with mask for the given supernetwork starting by a specific netid"
    
    def handle(self, *args, **options):
        supernetwork4 = IPv4Network(unicode(args[0]))
        supernetwork6 = IPv6Network(unicode(args[2]))
        mask4 = int(args[1])
        mask6 = int(args[3])
        subnets4 = supernetwork4.subnets(new_prefix=mask4)
        netid = int(args[4])
        self.stdout.write("This will generate {nets} new networks, Enter to continue, CTRL-C to cancel".format(nets=len(list(subnets4))))
        subnets4 = supernetwork4.subnets(new_prefix=mask4)
        subnets6 = supernetwork6.subnets(new_prefix=mask6)
        raw_input()
        self.stdout.write("Continuing...")
        for subnet4 in subnets4:
            subnet6 = subnets6.next()
            self.stdout.write("Generated network {network4} and {network6}".format(network4=subnet4, network6=subnet6))
            network = Network()
            network.netid = netid
            network.description = "Generated network {network4} and {network6}".format(network4=subnet4, network6=subnet6)
            network.ipv4_address = str(subnet4.network_address)
            network.ipv6_address = str(subnet6.network_address)
            network.ipv4_mask = subnet4.prefixlen
            network.ipv6_mask = subnet6.prefixlen
            network.save()
            netid = netid + 1