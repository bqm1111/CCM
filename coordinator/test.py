import socket
import netifaces
import agent.utils as utils
# print(netifaces.ifaddresses('usb0'))
print(utils.has_ip_address("172.21.100.242"))
print(utils.has_ip_address("172.21.100.243"))
