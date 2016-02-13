# avahi-indicator
Indicator that shows services advertised on the network with Zeroconf/Bonjour/Avahi, written in Python

![menu](https://cloud.githubusercontent.com/assets/2480569/13030383/223c9c06-d2a9-11e5-8760-4f5e6d63856f.jpg)

## Installation

As long as an [AppImage](http://appimage.org) does not exist yet, the simplest way on Ubuntu is

```
sudo apt-get install avahi-discover
wget https://raw.githubusercontent.com/probonopd/avahi-indicator/master/avahi-indicator.py
python avahi-indicator.py
```

## TODO

 * Create [AppImage](http://appimage.org)
 * Support more services (currently the menu shows only service types for which an action is configured (e.g., http(s), ssh, sftp-ssh, smb)
 * Test on other GNOME systems than Ubuntu
 * Sort menu (by service type and name)
 * Remove services from the menu that are no longer there
 * Support multiple domains
