# -*- coding: utf-8 -*-
from naomi import plugin
from naomi import profile
from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6
from num2words import num2words


def IPv4Address2Words(ip_address):
    language = profile.get('language', 'en_US')
    blocks = ip_address.split('.')
    return " ".join([
        num2words(blocks[0], lang=language),
        "dot",
        num2words(blocks[1], lang=language),
        "dot",
        num2words(blocks[2], lang=language),
        "dot",
        num2words(blocks[3], lang=language)
    ])


class Plugin(plugin.SpeechHandlerPlugin):
    def intents(self):
        _ = self.gettext
        return {
            'CheckNetworkIntent': {
                'locale': {
                    'en-US': {
                        'templates': [
                            "ARE YOU CONNECTED",
                            "ARE YOU CONNECTED TO THE NETWORK",
                            "ARE YOU CONNECTED TO THE INTERNET",
                            "DO YOU HAVE A CONNECTION",
                            "DO YOU HAVE A NETWORK CONNECTION",
                            "DO YOU HAVE AN INTERNET CONNECTION"
                        ]
                    }
                },
                'action': self.handle
            },
            'IPAddressIntent': {
                'locale': {
                    'en-US': {
                        'templates': [
                            "DO YOU HAVE AN IP ADDRESS",
                            "WHAT IS YOUR NETWORK ADDRESS",
                            "WHAT IS YOUR IP ADDRESS",
                            "WHAT IS YOUR INTERNET ADDRESS"
                        ]
                    }
                },
                "action": self.handle_ipaddress
            }
        }

    def handle(self, intent, mic):
        IPAddresses = self.getIPAddresses()
        if len(IPAddresses) < 1:
            mic.say(self.gettext("No, I am not connected."))
        else:
            if len(IPAddresses) == 1:
                # One interface
                for interface in IPAddresses:
                    if(len(IPAddresses[interface]) == 1):
                        # One interface, one protocol
                        # Yes, I am connected to the ipv4 network. My IP address is 10.42.0.120.
                        for protocol in IPAddresses[interface]:
                            IPAddressWords = IPAddresses[interface][protocol]
                            if protocol == "ipv4":
                                IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                            mic.say(self.gettext("Yes, I am connected to the {} network. My IP address is {}.").format(protocol, IPAddresses[interface][protocol]))
                    else:
                        # One interface, multiple protocols
                        # Yes, I am connected to the network. My ipv4 address is 10.42.0.120. My ipv6 address is fe80::1.
                        utterance1 = ""
                        for protocol in IPAddresses[interface]:
                            IPAddressWords = IPAddresses[interface][protocol]
                            if protocol == "ipv4":
                                IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                            utterance1 = self.gettext('{} My {} address is {}.').format(utterance1, protocol, IPAddressWords)
                        mic.say(self.gettext("Yes, I am connected to a network. {}").format(utterance1))
            else:
                # multiple interfaces
                # Yes, I am connected to 2 networks. On the wlan1 interface, my ipv4 address is 192.196.0.12 and my ipv6
                mic.say(self.gettext("Yes, I am connected to {} networks.").format(len(IPAddresses)))
                for interface in IPAddresses:
                    utterance1 = ""
                    protocol_number = 0
                    for protocol in IPAddresses[interface]:
                        protocol_number += 1
                        if(protocol_number != 1):
                            utterance1 = self.gettext("{}and ").format(utterance1)
                        IPAddressWords = IPAddresses[interface][protocol]
                        if protocol == "ipv4":
                            IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                        utterance1 = self.gettext("{}my {} address is {}").format(utterance1, protocol, IPAddressWords)
                    mic.say(self.gettext("On the {} interface, {}.").format(interface, utterance1))

    def handle_ipaddress(self, intent, mic):
        IPAddresses = self.getIPAddresses()
        if(len(IPAddresses) < 1):
            mic.say(self.gettext("I am not currently connected to any networks."))
        elif len(IPAddresses) == 1:
            # One interface
            for interface in IPAddresses:
                if(len(IPAddresses[interface]) == 1):
                    # One interface, one protocol
                    # My IP address is 10.42.0.120.
                    for protocol in IPAddresses[interface]:
                        IPAddressWords = IPAddresses[interface][protocol]
                        if protocol == "ipv4":
                            IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                        mic.say(self.gettext("My IP address is {}.".format(IPAddressWords)))
                else:
                    # One interface, multiple protocols
                    # My ipv4 address is 10.42.0.120. My ipv6 address is fe80::1.
                    utterance1 = ""
                    for protocol in IPAddresses[interface]:
                        IPAddressWords = IPAddresses[interface][protocol]
                        if protocol == "ipv4":
                            IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                        utterance1 = self.gettext('{}My {} address is {}. ').format(utterance1, protocol, IPAddressWords)
                    mic.say(utterance1)
        else:
            # multiple interfaces
            # On the wlan1 interface, my ipv4 address is 192.196.0.12 and my ipv6 address is fe80::1
            for interface in IPAddresses:
                utterance1 = ""
                protocol_number = 0
                for protocol in IPAddresses[interface]:
                    protocol_number += 1
                    if(protocol_number != 1):
                        utterance1 = self.gettext("{}and ").format(utterance1)
                    IPAddressWords = IPAddresses[interface][protocol]
                    if protocol == "ipv4":
                        IPAddressWords = IPv4Address2Words(IPAddresses[interface][protocol])
                    utterance1 = self.gettext("{}my {} address is {}").format(utterance1, protocol, IPAddressWords)
                mic.say(self.gettext("On the {} interface, {}.").format(interface, utterance1))

    # https://stackoverflow.com/questions/270745/how-do-i-determine-all-of-my-ip-addresses-when-i-have-multiple-nics
    @staticmethod
    def getIPAddresses():
        IPAddresses = {}
        for interface in interfaces():
            if interface != 'lo':
                if(AF_INET in ifaddresses(interface)):
                    for link in ifaddresses(interface)[AF_INET]:
                        if interface not in IPAddresses:
                            IPAddresses[interface]={}
                        IPAddresses[interface]['ipv4']=link['addr']
                if(AF_INET6 in ifaddresses(interface)):
                    for link in ifaddresses(interface)[AF_INET6]:
                        # Filter out addresses that are unspecified(::), loopback(::1), link local (fe80) or multicast (ff00)
                        if(link['addr'][:4] not in ('::','::1','fe80','ff00')):
                            if interface not in IPAddresses:
                                IPAddresses[interface]={}
                            IPAddresses[interface]['ipv6']=link['addr']
        return IPAddresses
