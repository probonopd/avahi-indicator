# avahi-indicator
avahi-indicator is an [AppIndicator](https://unity.ubuntu.com/projects/appindicators/) that shows services advertised on the network with [Zeroconf](https://en.wikipedia.org/wiki/Zero-configuration_networking)/[Bonjour](https://en.wikipedia.org/wiki/Bonjour_%28software%29)/[Avahi](https://en.wikipedia.org/wiki/Avahi_%28software%29), written in Python. Network services show up in the Ubuntu menu bar, and you can choose a service from a dropdown menu. This will open the corresponding service (e.g., opens a web browser, a SSH shell, a SFTP connection, etc.)

![menu](https://cloud.githubusercontent.com/assets/2480569/13030383/223c9c06-d2a9-11e5-8760-4f5e6d63856f.jpg)

## Installation

As long as an [AppImage](http://appimage.org) does not exist yet, the simplest way on Ubuntu is

```
sudo apt-get update
sudo apt-get -y install avahi-daemon python2.7 python-avahi python-dbus
wget https://raw.githubusercontent.com/probonopd/avahi-indicator/master/avahi-indicator.py
python avahi-indicator.py
```

## TODO

Pull requests welcome!

 * Solve [org.freedesktop.Avahi.TimeoutError](https://lists.freedesktop.org/archives/avahi/2010-May/001886.html)
 * Sort list of service names in the menu, and sort list of services in the menu
 * If a service is announced on the network after avahi-indicator is already launched, then a popup notification should appear, informing about the new service. However apparently avahi-indicator does not get informed (yet) when new services appear on the network after avahi-indicator has been launched (FIXME)
 * If a menu item is selected, then we should check if the service is still responding and if it is not, remove the corresponding menu entry or trigger a complete discovery (the device might have been powered off and no longer available)
 * Handle devices going away (are they "de-published")?
 * Support actions on more services (currently the menu shows only service types for which an action is configured (e.g., http(s), ssh, sftp-ssh, smb)
 * Test on other GNOME systems than Ubuntu
 * Sort menu (by service type and name)
 * Remove services from the menu that are no longer there
 * Support multiple domains
 * Create [AppImage](http://appimage.org)
