# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
def ip2hex(ip):
    '''
    Converts an ip to a hex value that can be used with a hex bit mask
    '''
    parts = ip.split(".")
    if len(parts) != 4: return None
    ipv = 0
    for part in parts:
        try:
            p = int(part)
            if p < 0 or p > 255: return None
            ipv = (ipv << 8) + p
        except:
            return None
    return ipv

def str_to_ipmask(ipmask):
    '''
    Converts a string with the notation ip/mask (e.g. 192.168.1.1/24 or 192.168.1.1/255.255.255.0) to an hex mask
    '''
    v = ipmask.split("/")
    if len(v) > 2: raise Exception("bad mask format")
    mask_ip = ip2hex(v[0])
    if mask_ip is None: raise Exception("bad mask format")
    mask = v[1] if len(v) == 2 else 32
    try:
        mask = (0xffffffff00000000 >> int(mask)) & 0xffffffff
    except:
        mask = ip2hex(v[1])
    
    if mask is None: raise Exception("bad mask format")
    return mask_ip, mask


def ip_in_ip_mask(ip, mask_ip, mask):
    '''
    Checks whether an ip is contained in an ip subnet where the subnet is stated as an ip in the dotted format, and a hex mask
    '''
    ip = ip2hex(ip)
    if ip is None: raise Exception("bad ip format")
    if (mask_ip & mask) == (ip & mask):
        return True
    return False

def ip_in_ipmask(ip, ipmask):
    '''
    Checks whether an ip is contained in an ip subnet where the subnet is a string with the notation ip/mask (e.g. 192.168.1.1/24 or 192.168.1.1/255.255.255.0)
    '''
    mask_ip, mask = str_to_ipmask(ipmask)
    return ip_in_ip_mask(ip, mask_ip, mask)

def check_mac(original_mac):
    '''
    Checks the format of a MAC address and returns it without double-colons and in capital letters, if it is correct. Otherwise it returns None.
    * it accepts the format of the double colons and a single hex string
    '''
    mac = (original_mac.upper()).strip()
    parts = mac.split(':')
    if len(parts) == 6:
        # let's think that it is a : separated mac
        for p in parts:
            if len(p) != 2:
                return None
        mac = ''.join(parts)
    elif len(parts) > 1:
        return None
    for c in mac:
        if c not in '0123456789ABCDEF':
            return None
    return mac

def check_ip(original_ip):
    '''
    Checks the format of an IP address and returns it if it is correct. Otherwise it returns None.
    ''' 
    ip = original_ip.strip()
    parts = ip.split('.')
    if len(parts) != 4:
        return None
    for p in parts:
        try:
            p = int(p)
            if (p < 0) or (p > 255):
                return None
        except:
            return None
    return ip
