"""
    Manoto TV Kodi Plugin - written by Ali Jannatpour (google me)

    Credits:
	http://kodi.wiki/view/Audio-video_add-on_tutorial
	https://www.codecademy.com/glossary/python
	http://kodi.wiki/view/List_of_built-in_functions
	http://kodi.wiki/view/HOW-TO:Write_python_scripts
"""

import xbmcplugin,xbmcgui,xbmcaddon
import urllib,urlparse,urllib2,re,os,cookielib,string
import json
import requests
from urlparse import urljoin
from bs4 import BeautifulSoup

# plugin constants

__plugin__ = "Manoto TV"
__author__ = "alij"
__url__ = ""
__credits__ = "Kodi Wikis"
__version__ = "0.5.0"


# global data

addon = xbmcaddon.Addon('plugin.video.manototv')
addonname = addon.getAddonInfo('name')
addon_handle = int(sys.argv[1])
path = addon.getAddonInfo('path')
base = sys.argv[0]
args = urlparse.parse_qs(sys.argv[2][1:])

icon = xbmc.translatePath(os.path.join(path, 'icon.png'))

# parameters

__site_baseurl = "https://www.manototv.com/"

# global code

#xbmcplugin.setContent(addon_handle, 'movies')

requests.packages.urllib3.disable_warnings()

cookies = cookielib.CookieJar()
http_request = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

#utility functions

def alert(msg):
	dialog = xbmcgui.Dialog()
	dialog.ok(addonname, msg)

def getDoc(url):
	headers = {'User-Agent':'Mozilla/5.0'}
	page = requests.get(url)
	return page.text

def getDOM(url):
	return BeautifulSoup(getDoc(url), 'html.parser')

def play(video):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	playlist.add(video)
	xbmc.Player().play(playlist)
	return True

def additem(title, url, icon, isfolder, isplayable):
	li = xbmcgui.ListItem(title)
	li.setInfo(type='Video', infoLabels={'Title' : title})
	if not(icon == None):
		li.setThumbnailImage(icon)
	if isplayable == True:
		li.setProperty("IsPlayable","true")
	if isfolder == None:
		isfolder = True
	xbmcplugin.addDirectoryItem(handle=addon_handle,
				    url=url,
                	            listitem=li,
                                    isFolder=isfolder)

def addEOI():
	xbmcplugin.endOfDirectory(addon_handle)

# general functions

def build_url(query):
    return base + '?' + urllib.urlencode(query)

def getArg(key):
	val = args.get(key, None)
	return None if val == None else val[0]

# playlist functions

def parsePlaylist(playlist): # Credits to  micahg, babak
	resp = http_request.open(playlist)
        data = resp.read()
	base = playlist[0:string.rfind(playlist,'/') + 1]
	lines = data.split('\n')
	if lines[0] != "#EXTM3U":
		return None
	streams = {}
        bandwidth = ""
	for line in lines:
		if line == '#EXTM3U':
			continue
		m = re.search("BANDWIDTH=(\d+)", line)
		if m:
			bandwidth = m.group(1)
		elif len(line) > 0 and len(bandwidth) > 0:
			streams[bandwidth] = (("" if line.lower().startswith("http") else base) + line + 
						("" if len(playlist.split("?")) != 2 else "&" + playlist.split("?")[1])).strip()
	return streams

# site specific functions

def getCategories():
	result = []
	node = getDOM(urljoin(__site_baseurl, "/schedule"))
	node = node.find("div", {"class" : "ShowPanelContent"})
	if not(node == None):
		node = node.findAll("div", {"class" : "Header"})
	if not(node == None):
		for link in node:
			url = None
			title = link.text
			entitle = link['title']
			img = None
			result.append({'title': title, 'entitle': entitle, 'img': img, 'url': url})
	#result.sort(key=lambda i: i['title'], reverse=False)
	return result

def getPrograms(category):
	result = []
	node = getDOM(urljoin(__site_baseurl, "/schedule"))
	node = node.find("div", {"class" : "ShowPanelContent"})
	if not(node == None):
		node = node.find("div", {"class" : "Header", "title" : category})
	if not(node == None):
		node = node.parent.findAll("a")
	for link in node:
		url = link['href']
		title = link.text
		img = None
		result.append({'title': title, 'img': img, 'url': url})
	#result.sort(key=lambda i: i['title'], reverse=False)
	return result

def getVideoLinks(container_url):
	result = []
	node = getDOM(urljoin(__site_baseurl, container_url))
	node = node.find("span", {"title" : "Video Categories"})
	if not(node == None):
		node = node.parent.parent.parent.parent.findAll("a")
	for link in node:
		title = link.find('span', {"class" : "Title"}).text
		url = link['href']
		img = link.find('img')['src']
		result.append({'title': title, 'img': img, 'url': url})
	return result

def resolveVideo(page_url):
	node = getDOM(urljoin(__site_baseurl, page_url))
	#node = node.find("video", {"id" : "HTML5player"})
	node = node.find("source")
	link = node['src']
	#doc = getDoc(urljoin(__site_baseurl, page_url))
	#link = re.search('(?<=<source\ssrc=\")[^\"]*', doc).group(0)
	#link = re.search('file\s*\:\s*\"https\:[^\"]*', doc).group(0)
	#link = link[link.find('https'):]
	return link

def getLiveLink():
	page_url = '/live'
	'''
	node = getDOM(urljoin(__site_baseurl, page_url))
	link = node.find("video")
	if not(link == None):
		link = link.find('source')
		link = link['src']
	streams = parsePlaylist(link)
	if streams == None:
		alert('Error retreiving playlist')
		return None
	bitrates = []
   	for k in streams.keys():
       		bitrates.append(int(k))
	bitrates.sort()
   	bitrates.reverse()
	url = streams[str(bitrates[0])]
	'''
	'''
	doc = getDoc(urljoin(__site_baseurl, page_url))
	link = re.search('file\s*\:\s*\"https\:[^\"]*', doc).group(0)
	link = link[link.find('https'):]
	'''
	node = getDOM(urljoin(__site_baseurl, page_url))
	link = node.find("video")
	if not(link == None):
		link = link.find('source')
		link = link['src']
	return link

# main

def main():
	if not (getArg('manoto-special') is None):
		play(getLiveLink())
	elif not (getArg('manoto-category') is None):
		progs = getPrograms(getArg('manoto-category'))
		for p in progs:
			additem(title=p['title'],
				url= build_url({"manoto-folder": p['url']}),
				icon=p['img'], isfolder=True, isplayable=False)
		addEOI()
	elif not (getArg('manoto-folder') is None):
		vidoes = getVideoLinks(getArg('manoto-folder'))
		for v in vidoes:
			additem(title=v['title'], 
				url=build_url({"manoto-link": v['url']}), 
				icon=v['img'], isfolder=False, isplayable=False)
		addEOI()
	elif (getArg('manoto-link') is None):
		additem(title='Live TV - پخش زنده', 
			url=build_url({"manoto-special": 'live'}), 
			icon=icon, isfolder=False, isplayable=False)
		cats = getCategories()
		for c in cats:
			additem(title=c['entitle'] + ' - '+ c['title'], 
				url=build_url({"manoto-category": c['entitle']}),
				icon=c['img'], isfolder=True, isplayable=False)
		addEOI()
	else:
		play(resolveVideo(getArg('manoto-link')))
	return True

try:
	main()
except Exception, e:
	alert("ERR:" + str(e))
	#alert('Error retrieving data from Manoto TV website')

