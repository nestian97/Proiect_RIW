import dns
import dns.resolver
import socket

answers = dns.resolver.Resolver().query('http://riweb.tibeica.com', 'MX')
for rdata in answers:
    print ('Host', rdata.exchange, 'has preference', rdata.preference)