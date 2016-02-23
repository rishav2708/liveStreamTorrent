import os
import sys
import tabulate
import urllib
import struct
import socket
import re
from udptor import UDPTracker
from random import randrange
from torrentTest import getInfoUDP
from bs4 import BeautifulSoup as BS 
cliSock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
tracker = "tracker.istole.it"
port = 80
def download(metadata):
	tracker1=metadata["tr"][0]
	port=int(re.findall("[0-9]+",tracker1)[0])
	host=re.findall("[^0-9]+",tracker1)[0]
	host=host[:-1]
	host=host[6:]
	print host,port
	cliSock.connect((host,port))
	connection_id=0x41727101980
	transaction_id=randrange(1,65535)
	packet=struct.pack(">QLL",connection_id, 0,transaction_id)
	cliSock.send(packet)
	res=cliSock.recv(16)
	action,transaction_id,connection_id=struct.unpack(">LLQ",res)
	torrent_hash=metadata["hash_info"]
	print action,transaction_id,connection_id
	packet_hash=torrent_hash.decode("hex")
	print packet_hash
	#for info_hash in torrent_hash:
		#packet_hash=packet_hash+info_hash.decode('hex')
	packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hash
	cliSock.send(packet)
	res=cliSock.recv(8 + 12*len(torrent_hash))
	index = 8
	print res
	for infohash in torrent_hash:
		seeders, completed, leechers = struct.unpack(">LLL", res[index:index+12])
		print seeders,completed,leechers
		index = index + 12 
	info_hash = packet_hash
	peer_id = "ABCDEFGHIJKLMNOPQRST"
	action = 0
	downloaded = 0
	left = 0
	uploaded = 0
	event = 2
	ip = 0
	key = 0
	num_want = 10
	port = 6800
	args=[info_hash,peer_id,action,downloaded,left,uploaded,event,ip,key,num_want,port]
	payload = struct.pack('!20s20sQQQLLLLH', *args)
	announce_packet=struct.pack(">QLL", connection_id, 1, transaction_id)+payload
	cliSock.send(announce_packet)
	res=cliSock.recv(1024)
	print res
	action = struct.unpack("!LLLLLLH", res)
	print action
def parse_magnet_uri(magnetLink):
	magnetLink=magnetLink[8:]
	comp=magnetLink.split("&")
	metaData={}
	bithEncode=comp[0].split("=")
	metaData[bithEncode[0]]=bithEncode[1]
	name=comp[1].split("=")
	metaData[name[0]]=urllib.unquote(name[1])
	metaData["tr"]=[]
	for i in range(2,len(comp)):
		trackEncoded=comp[i].split("=")[1]
		trackDecoded=urllib.unquote(trackEncoded)
		metaData["tr"].append(trackDecoded)
	metaData["hash_info"]=bithEncode[1][9:]
	return metaData
text=raw_input("Input movie: ")
text=text.replace(" ","+")
url="https://piratebays.co/s/?q="+text
print url
src=os.system("wget "+url+"  -O abc.html")
html=open("abc.html").read()
print html
source=BS(html)
links=source.find_all("a",attrs={"class","detLink"})
table=[]
mapper={}
for i in range(len(links)):
	li=[i+1,links[i].text]
	mapper[i+1]=links[i]["href"]
	table.append(li)
_table=tabulate.tabulate(table,headers=["No","Title"])
print _table
#choose torrent
choice=input("Choose torrent>> ")
downloadUrl="https://piratebays.co"+mapper[choice]
os.system("wget '"+downloadUrl+"' -O download.html")
fp=open("download.html").read()
source1=BS(fp)
magnetLink=source1.find_all("div",attrs={"class","download"})
magnet_uri=magnetLink[0].find_all("a")[0]["href"]
metadata=parse_magnet_uri(magnet_uri)
#download(metadata)
#getInfoUDP([metadata["hash_info"]])
announce_url=metadata["tr"][0]
info_hash=metadata["hash_info"]
os.system("peerflix '"+magnet_uri+"' --vlc")