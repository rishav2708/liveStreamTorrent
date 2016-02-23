import socket
import struct   
from random import randrange #to generate random transaction_id
from urllib import urlopen
import re

tracker = "tracker.openbittorrent.com"
port = 80
#torrent_hash = ["3ebde329f208b9e2e81c8e0f80d14384d5f416e4", "3ac9002ce1a7d5dde2c02b7cf9dc9e0f15eda7cb", "00e058f6629a19b42458af4dea5f6b9e2ebe8e25"]
torrent_hash=["3ebde329f208b9e2e81c8e0f80d14384d5f416e4"]
torrent_details = {}

def get_torrent_name(infohash):
    url = "http://torrentz.me/" + infohash
    p = urlopen(url)
    page = p.read()
    c = re.compile(r'<h2><span>(.*?)</span>')
    return c.search(page).group(1)

def pretty_show(infohash):
    print "Torrent Hash: ", infohash
    try:
        print "Torrent Name (from torrentz): ", get_torrent_name(infohash)
    except:
        print "Coundn'f find torrent name"
    print "Seeds, Leechers, Completed", torrent_details[infohash] 
    print

def getInfoUDP(torrent_hash):
    #Create the socket
    clisocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clisocket.connect((tracker, port))

    #Protocol says to keep it that way
    connection_id=0x41727101980
    #We should get the same in response
    transaction_id = randrange(1,65535)

    packet=struct.pack(">QLL",connection_id, 0,transaction_id)
    clisocket.send(packet)
    res = clisocket.recv(16)
    action,transaction_id,connection_id=struct.unpack(">LLQ",res)

    packet_hashes = ""
    for infohash in torrent_hash:
        packet_hashes = packet_hashes + infohash.decode('hex')

    packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes

    clisocket.send(packet)
    res = clisocket.recv(8 + 12*len(torrent_hash))

    index = 8
    for infohash in torrent_hash:
        seeders, completed, leechers = struct.unpack(">LLL", res[index:index+12])
        torrent_details[infohash] = (seeders, leechers, completed)
        pretty_show(infohash)
        index = index + 12 