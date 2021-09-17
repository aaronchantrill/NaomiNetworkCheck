# -*- coding: utf-8 -*-
from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6
from naomi import plugin

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
            mic.say("No, I am not connected.")
        else:
            if len(IPAddresses) == 1:
                # One interface
                for interface in IPAddresses:
                    if(len(IPAddresses[interface]) == 1):
                        # One interface, one protocol
                        # Yes, I am connected to the ipv4 network. My IP address is 10.42.0.120.
                        for protocol in IPAddresses[interface]:
                            mic.say("Yes, I am connected to the {} network. My IP address is {}.".format(protocol, IPAddresses[interface][protocol]))
                    else:
                        # One interface, multiple protocols
                        # Yes, I am connected to the network. My ipv4 address is 10.42.0.120. My ipv6 address is fe80::1.
                        utterance1 = ""
                        for protocol in IPAddresses[interface]:
                            utterance1 = '{} My {} address is {}.'.format(utterance1, protocol, IPAddresses[interface][protocol])
                        mic.say("Yes, I am connected to a network. {}".format(utterance1))
            else:
                # multiple interfaces
                # Yes, I am connected to 2 networks. On the wlan1 interface, my ipv4 address is 192.196.0.12 and my ipv6
                mic.say("Yes, I am connected to {} networks.".format(len(IPAddresses)))
                for interface in IPAddresses:
                    utterance1 = ""
                    protocol_number = 0
                    for protocol in IPAddresses[interface]:
                        protocol_number += 1
                        if(protocol_number != 1):
                            utterance1 = "{}and ".format(utterance1)
                        utterance1 = "{}my {} address is {}".format(utterance1, protocol, IPAddresses[interface][protocol])
                    mic.say("On the {} interface, {}.".format(interface, utterance1))

    def handle_ipaddress(self, intent, mic):
        IPAddresses = self.getIPAddresses()
        if(len(IPAddresses) < 1):
            mic.say("I am not currently connected to any networks.")
        elif len(IPAddresses) == 1:
            # One interface
            for interface in IPAddresses:
                if(len(IPAddresses[interface]) == 1):
                    # One interface, one protocol
                    # My IP address is 10.42.0.120.
                    for protocol in IPAddresses[interface]:
                        mic.say("My IP address is {}.".format(protocol, IPAddresses[interface][protocol]))
                else:
                    # One interface, multiple protocols
                    # My ipv4 address is 10.42.0.120. My ipv6 address is fe80::1.
                    utterance1 = ""
                    for protocol in IPAddresses[interface]:
                        utterance1 = '{}My {} address is {}. '.format(utterance1, protocol, IPAddresses[interface][protocol])
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
                        utterance1 = "{}and ".format(utterance1)
                    utterance1 = "{}my {} address is {}".format(utterance1, protocol, IPAddresses[interface][protocol])
                mic.say("On the {} interface, {}.".format(interface, utterance1))

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
