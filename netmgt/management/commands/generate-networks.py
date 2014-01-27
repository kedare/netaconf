from django.core.management.base import BaseCommand, CommandError
from netmgt.models import Network
from ipaddress import *

class Command(BaseCommand):
    args = "<supernetwork/mask> <subnetmask> <firstnetid>"
    help = "Generates all the subnets with mask for the given supernetwork starting by a specific netid"
    
    def handle(self, *args, **options):
        supernetwork = IPv4Network(unicode(args[0]))
        subnet_mask = int(args[1])
        subnets = supernetwork.subnets(new_prefix=subnet_mask)
        netid = int(args[2])
        self.stdout.write("This will generate {nets} new networks, Enter to continue, CTRL-C to cancel".format(nets=len(list(subnets))))
        subnets = supernetwork.subnets(new_prefix=subnet_mask)
        raw_input()
        self.stdout.write("Continuing...")
        for subnet in subnets:
            self.stdout.write("Generating network {network}".format(network=subnet))
            network = Network()
            network.netid = netid
            network.description = "Generated network {network}".format(network=subnet)
            network.address = str(subnet.network_address)
            network.mask = subnet.prefixlen
            network.save()
            netid = netid + 1