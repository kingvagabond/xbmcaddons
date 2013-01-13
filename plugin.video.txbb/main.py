# -*- coding: utf-8 -*-
# Version 0.0.2: Frodo tested
# Version 0.0.3: Fixed a bug when the playlist contains longer channel strings
import xbmcplugin, xbmcgui, urllib, re, urllib2, string, urlparse

def error(message):
    addon_id=urlparse.urlsplit(sys.argv[0])[1]
    err_msg='[%s] ERROR: %s' % (addon_id, message)
    xbmcgui.Dialog().ok('错误', '不好意思，出错了！', err_msg)
    sys.exit(1)

def getPageData(url):
    user_agent='Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
    req=urllib2.Request(urllib.unquote(url))
    req.add_header('User-Agent', user_agent)
    try:
        response=urllib2.urlopen(req)
    except:
        error(url + ': URL不能打开')
    data=response.read()
    response.close()
    items=re.compile('meta charset="(.+?)"').findall(data)
    return data

def getVideoURL(preUrl):
    videoData = getPageData(preUrl)
    videoListRex = re.compile('\[\[(.+?)]]', re.DOTALL)
    videoList = videoListRex.search(videoData)
    videlEleList = []
    if videoList != None:
        videoListData = videoList.group()
        videoEleRex = re.compile('\"[-_\w]{11}\"', re.DOTALL)
        videoEleList = videoEleRex.findall(videoListData)
    return videoEleList

def getMenuList(pageUrl, menuLevel):
    pageData = getPageData(pageUrl)
    menuList = [];

    rex = ['<ul(.+?)</ul>', '<li(.+?)</li>', '<a href="(.+?)">(.+?)</a>', 
    'class="movie-poster" src="(.+?)"(.+?)<h2>(.+?)<i(.+?)<a class="btn playbtn" href="(.+?)"']
    if menuLevel == 2:
        menuList = getVideoURL(pageUrl)
        return menuList
    else:
        m1=re.compile(rex[0], re.DOTALL).findall(pageData)
        for ul in m1:
            m2=re.compile(rex[1], re.DOTALL).findall(ul)
            for li in m2:
                if menuLevel == 0:
                    m3=re.compile(rex[2], re.DOTALL).findall(li)
                    if len(m3) > 0:
                        for href, category in m3:
                            menuList.append((category, href))
                elif menuLevel == 1:
                    m4=re.compile(rex[3], re.DOTALL).findall(li)
                    if len(m4) > 0:
                        for videoThumb, videoInfo1, videoName, videoInfo, videoHref in m4:
                            menuList.append((videoName.strip(), videoHref, videoThumb))
        return menuList

## Entrance point:
rootURL = 'http://v.netstartv.com/'
handle = int(sys.argv[1])
dirLevel = 0
isFolder = True
if sys.argv[2] != '':
    dirLevel = int(sys.argv[2][1:2])
    pageURL = sys.argv[2][3:]

menu = []
itemNumber = 1
youtubeURL = 'plugin://plugin.video.youtube/?action=play_video&autoplay=1&videoid=%s'
if dirLevel == 0:
    menu = getMenuList(rootURL, 0)
    for menuItem in menu:
        listitem = xbmcgui.ListItem( menuItem[0] )
        xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?' + str(dirLevel + 1) + '&' + menuItem[1], listitem, True)
elif dirLevel == 1:
    menu = getMenuList(pageURL, 1)
    for menuItem in menu:
        listitem = xbmcgui.ListItem( menuItem[0], thumbnailImage=menuItem[2])
        xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?' + str(dirLevel + 1) + '&' + menuItem[1], listitem, True)
elif dirLevel == 2:
    menu = getMenuList(pageURL, 2)
    for menuItem in menu:
        listitem = xbmcgui.ListItem( str(itemNumber) )
        itemNumber = itemNumber + 1
        xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?' + str(dirLevel + 1) + '&' + youtubeURL % menuItem[1:12], listitem, False)
elif dirLevel == 3:
    xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(pageURL)

xbmcplugin.endOfDirectory(handle)