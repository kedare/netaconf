NETACONF
============

Does not work on Python 3.3, developped under Python 2.7 and Django 1.6

This Django project allows you  to configure a network on a router and a switch connected to it.
It connect via SSH to the devices.
All the configuration is done by configuring objects in the Django admin area (by default http://localhost/admin )

First you must configure the database informations in settings.py,
then launch :

	python manage.py syncdb

to create the database.

Then create the networks by using (here is an example) :

	python manage.py generate-networks 10.0.0.0/24 28 cafe::/48 64 100
	This will generate 16 new networks, Enter to continue, CTRL-C to cancel
	
	Continuing...
	Generated network 10.0.0.0/28 and cafe::/64
	Generated network 10.0.0.16/28 and cafe:0:0:1::/64
	Generated network 10.0.0.32/28 and cafe:0:0:2::/64
	Generated network 10.0.0.48/28 and cafe:0:0:3::/64
	Generated network 10.0.0.64/28 and cafe:0:0:4::/64
	Generated network 10.0.0.80/28 and cafe:0:0:5::/64
	Generated network 10.0.0.96/28 and cafe:0:0:6::/64
	Generated network 10.0.0.112/28 and cafe:0:0:7::/64
	Generated network 10.0.0.128/28 and cafe:0:0:8::/64
	Generated network 10.0.0.144/28 and cafe:0:0:9::/64
	Generated network 10.0.0.160/28 and cafe:0:0:a::/64
	Generated network 10.0.0.176/28 and cafe:0:0:b::/64
	Generated network 10.0.0.192/28 and cafe:0:0:c::/64
	Generated network 10.0.0.208/28 and cafe:0:0:d::/64
	Generated network 10.0.0.224/28 and cafe:0:0:e::/64
	Generated network 10.0.0.240/28 and cafe:0:0:f::/64

Start the server with :

	python manage.py runserver

And connects to the admin area with the user you created during syncdb.

Do all the configuration you need (At least, 1 switch, 1 router, 1 uplink, 1 switch interface as uplink, 1 switch interface as access, 1 network)

Then to push to the devices :

	python manage.py configure

Example of required configuration on the devices :
--------------


Router :

	ip cef
	ip domain name lab.aforp
	ip name-server 8.8.8.8
	ipv6 unicast-routing
	ipv6 cef
	ip dns server
	ip nat inside source list nat-acl interface FastEthernet0/1.1 overload
	ip route 0.0.0.0 0.0.0.0 172.30.254.254

Switch :
Uplink must tag all vlans.

	interface GigabitEthernet0/1
		switchport mode trunk
		switchport trunk allowed vlan all