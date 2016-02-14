#! /usr/bin/python
# -*-python-*-
# Based on avahi-discover, a part of avahi.
#
# avahi is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# avahi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with avahi; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.

import re
import os, sys
import urllib2
import signal

from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3 as appindicator

import avahi, gettext, gobject, dbus, avahi.ServiceTypeDatabase

# It's really important to do this, else you won't see any events
try:
    from dbus import DBusException
    import dbus.glib
except ImportError, e:
    pass

from collections import OrderedDict

from gi.repository import Notify

import time

servicesdb = "/usr/share/avahi/service-types"

service_type_browsers = {}
service_browsers = {}

class Service(object):

    def __init__(self, interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags):
        self.interface = interface
        self.protocol = protocol
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.aprotocol = aprotocol
        self.address = address
        self.port = port
        self.txt = txt
        self.flags = flags
        self.command=None

	if(self.stype=="_http._tcp"):
		path=""
		for data in avahi.txt_array_to_string_array(self.txt):
			if (data.startswith("path=")):
				path = data[len("path="):]
		self.command="xdg-open http://%s:%i%s &" % (self.host, self.port, path)

	if(self.stype=="_https._tcp"):
		path=""
		for data in avahi.txt_array_to_string_array(self.txt):
			if (data.startswith("path=")):
				path = data[len("path="):]
		self.command="xdg-open https://%s:%i%s &" % (self.host, self.port, path)

	if(self.stype=="_ssh._tcp"):
		self.command="gnome-terminal -x ssh %s %i &" % (self.host, self.port)
		# TODO: Ask for username and password

	if(self.stype=="_sftp-ssh._tcp"):
		self.command="nautilus ssh://%s:%i &" % (self.host, self.port)

	if(self.stype=="_smb._tcp"):
		self.command="nautilus smb://%s:%i &" % (self.host, self.port)

class MyIndicator:

    def __init__(self):
    # Create Indicator with icon and label
        icon_image = "/usr/share/unity/icons/panel-shadow.png"
        self.start_time = time.clock()
        self.ind = appindicator.Indicator.new(
            "MagicNumber",
            icon_image,
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.services = []
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu_structure()
        self.new()

    def protoname(self,protocol):
        if protocol == avahi.PROTO_INET:
            return "IPv4"
        if protocol == avahi.PROTO_INET6:
            return "IPv6"
        return "n/a"

    def siocgifname(self, interface):
        if interface <= 0:
            return "n/a"
        else:
            return self.server.GetNetworkInterfaceNameByIndex(interface)

    def get_interface_name(self, interface, protocol):
        if interface == avahi.IF_UNSPEC and protocol == avahi.PROTO_UNSPEC:
            return "Wide Area"
        else:
            return str(self.siocgifname(interface)) + " " + str(self.protoname(protocol))

    def service_resolved(self, interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags):
        print "Service data for service '%s' of type '%s' in domain '%s' on %i.%i:" % (name, stype, domain, interface, protocol)
        print "\tHost %s (%s), port %i, TXT data: %s" % (host, address, port, str(avahi.txt_array_to_string_array(txt)))
        self.services.append(Service(interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags))
        secs_since_launch = (time.clock() - self.start_time)/60
        print("\t" + str(secs_since_launch) + " secs since launch")
        # Services that are added after 2 seconds after launch trigger a notification 
        if (secs_since_launch > 2.0):
            Notify.init("Avahi")
            Hello=Notify.Notification.new(name, stype, "dialog-information")
            Hello.show()
        self.rebuild_menu()

    def rebuild_menu(self):

        # TODO: Sort both the service names and the menu items for each service name

        for i in self.menu.get_children():
            self.menu.remove(i)

	stypes = []
        for service in self.services:
            stypes.append(service.stype)
        stypes = list(OrderedDict.fromkeys(stypes)) # Remove duplicates

        for stype in stypes:
            service_cleartext = self.lookup_type(stype)
            if not ((service_cleartext.startswith("_") or (service_cleartext.startswith("Workstation")))):
                self.menuitem = Gtk.MenuItem(service_cleartext)
                self.menuitem.set_sensitive(False)
                # self.menuitem.connect("activate", self.run, service.command)
                self.menuitem.show()
                self.menu.append(Gtk.SeparatorMenuItem())
                self.menu.append(self.menuitem)
                for service in self.services:
                    if(service.stype == stype):
                        self.menuitem = Gtk.MenuItem(service.name)
                        self.menuitem.connect("activate", self.run, service.command)
                        self.menuitem.show()
                        self.menu.append(self.menuitem)
        self.menu.show_all()

    def print_error(self, err):
        print "Error:", str(err)

    def lookup_type(self, stype):
        
        with open(servicesdb) as f:
            for line in f:
                if line.startswith(stype + ":"):
                    return line.split(":")[1].strip()

        return stype

    def run(self, sender, command):
        print(command)
	os.system(command)

    def new_service(self, interface, protocol, name, stype, domain, flags):
        print "Found service '%s' of type '%s' in domain '%s' on %i.%i." % (name, stype, domain, interface, protocol)
        if self.zc_ifaces.has_key((interface,protocol)) == False:
            ifn = self.get_interface_name(interface, protocol)
        self.server.ResolveService( int(interface), int(protocol), name, stype, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0), reply_handler=self.service_resolved, error_handler=self.print_error)

    def remove_service(self, interface, protocol, name, stype, domain, flags):
        print "Service '%s' of type '%s' in domain '%s' on %i.%i disappeared." % (name, stype, domain, interface, protocol)

    def new_service_type(self, interface, protocol, stype, domain, flags):
        global service_browsers

        # Are we already browsing this domain for this type?
        if service_browsers.has_key((interface, protocol, stype, domain)):
            return

        print "Browsing for services of type '%s' in domain '%s' on %i.%i ..." % (stype, domain, interface, protocol)

        b = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.ServiceBrowserNew(interface, protocol, stype, domain, dbus.UInt32(0))),  avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        b.connect_to_signal('ItemNew', self.new_service)
        b.connect_to_signal('ItemRemove', self.remove_service)

        service_browsers[(interface, protocol, stype, domain)] = b

    def browse_domain(self, interface, protocol, domain):
        global service_type_browsers

        # Are we already browsing this domain?
        if service_type_browsers.has_key((interface, protocol, domain)):
            return

        if self.stype is None:
            print "Browsing domain '%s' on %i.%i ..." % (domain, interface, protocol)

            try:
                b = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.ServiceTypeBrowserNew(interface, protocol, domain, dbus.UInt32(0))),  avahi.DBUS_INTERFACE_SERVICE_TYPE_BROWSER)
            except DBusException, e:
                print e
                error_msg("You should check that the avahi daemon is running.\n\nError : %s" % e)
                sys.exit(0)

            b.connect_to_signal('ItemNew', self.new_service_type)

            service_type_browsers[(interface, protocol, domain)] = b
        else:
            new_service_type(interface, protocol, stype, domain)

    def new_domain(self,interface, protocol, domain, flags):
        if self.zc_ifaces.has_key((interface,protocol)) == False:
            ifn = self.get_interface_name(interface, protocol)
            self.zc_ifaces[(interface,protocol)] = self.insert_row(self.treemodel, None, ifn,None,interface,protocol,None,domain)
        if self.zc_domains.has_key((interface,protocol,domain)) == False:
            self.zc_domains[(interface,protocol,domain)] = self.insert_row(self.treemodel, self.zc_ifaces[(interface,protocol)], domain,None,interface,protocol,None,domain)
        if domain != "local":
            self.browse_domain(interface, protocol, domain)

    def pair_to_dict(self, l):
        res = dict()
        for el in l:
            if "=" not in el:
                res[el]=''
            else:
                tmp = el.split('=',1)
                if len(tmp[0]) > 0:
                    res[tmp[0]] = tmp[1]
        return res

    def new(self):
        self.domain = None
        self.stype = None
        self.zc_ifaces = {}
        self.zc_types = {}
        self.services_browsed = {}

        try:
            self.bus = dbus.SystemBus()
            self.server = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
        except Exception, e:
            print "Failed to connect to Avahi Server (Is it running?): %s" % e
            sys.exit(1)

        if self.domain is None:
            self.browse_domain(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "local")

    def menu_structure(self):
        self.menu = Gtk.Menu()
        self.exit = Gtk.MenuItem("Exit")
        self.exit.connect("activate", self.quit)
        self.exit.show()
        self.menu.append(self.exit)
        self.ind.set_menu(self.menu)
        self.ind.set_label("Avahi","Avahi")

    def quit(self, widget):
        Gtk.main_quit()

if __name__ == "__main__":
    indicator = MyIndicator()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
