# -*- coding: utf-8 -*-
import alfred
import json
import urllib
import os
# import time

AK = 'PnoibPQYhICT4uvbtvOdXE2t'
QUERY_URL = {
    'location': 'http://api.map.baidu.com/location/ip?',
    'weather': 'http://api.map.baidu.com/telematics/v3/weather?',
}
QUERY_PARAM = {
    'location': {
        'ak': AK,
    },
    'weather': {
        'ak': AK,
        'location': '',
        'output': 'json',
    },
}


def PM2_5_rank(pm25):
    if pm25 < 0:
        return (u'查询出错', None)
    if pm25 <= 50:
        return (u'优', 'pm25green.png')
    if pm25 <= 100:
        return (u'良', 'pm25yellow.png')
    if pm25 <= 150:
        return (u'轻度污染', 'pm25orange.png')
    if pm25 <= 200:
        return (u'中度污染', 'pm25red.png')
    if pm25 <= 300:
        return (u'重度污染', 'pm25purple.png')
    if pm25 <= 500:
        return (u'严重污染', 'pm25brown.png')
    return (u'爆表', 'pm25brown.png')


def get_weather_icon_name(url):
    filename = url.split('/')[-1]
    if not os.path.isfile(filename):
        with open(filename, 'wb') as f:
            r = urllib.urlopen(url)
            f.write(r.read())
            r.close()
    return filename


def get_location():
    try:
        # if os.path.isfile('last_request_location.txt'):
        #     with open('last_request_location.txt', 'r+') as f:
        #         last_request_time = float(f.readline().strip('\n'))
        #         if abs(time.mktime(time.gmtime()) - last_request_time) < 900:
        #             last_location = f.readline().strie('\n')
        #             return last_location
        location_response = request_for('location')
    except Exception, e:
        print 'Err in get_location'
        print e
        raise
    location_response = location_response.decode('unicode_escape')
    location_response = unicode(location_response)
    # print repr(location_response)
    location_response = json.loads(location_response)
    return location_response['content']['address'].encode('utf8')


def request_for(url):
    global QUERY_PARAM, LOCATION
    if url == 'weather' and (not QUERY_PARAM['weather']['location']):
        QUERY_PARAM['weather']['location'] = get_location()
    query = QUERY_URL[url] + urllib.urlencode(QUERY_PARAM[url])
    try:
        r = urllib.urlopen(query)
        res = r.read()
        r.close()
    except Exception, e:
        print 'Err in request_for'
        print e
        raise
    return res


def get_weather(query=''):
    if query:
        global QUERY_PARAM
        QUERY_PARAM['weather']['location'] = query
    try:
        weather = json.loads(request_for('weather'))
        if weather['error']:
            raise
    except:
        return alfred.xml((alfred.Item(title=u'查询失败'),))
    weather = weather['results'][0]
    result = []
    pm25 = PM2_5_rank(int(weather['pm25']))
    pm25 = alfred.Item(
        title=''.join((
            u'%s  空气质量：' % weather['currentCity'],
            weather['pm25'], '  ', pm25[0],
        )),
        icon=pm25[1]
    )
    result.append(pm25)
    now = weather['weather_data'][0]
    now = alfred.Item(
        title=now['date'].replace(' ', ' ' * 4, 1),
        subtitle=''.join((
            now['weather'], u'，',
            now['wind'], u'，',
            u'气温：',
            now['temperature'],
        )),
        icon=(get_weather_icon_name(now['dayPictureUrl']), {'type': 'png'})
    )
    result.append(now)
    for data in weather['weather_data'][1:]:
        title = u'%s    %s' % (data['date'], data['weather'])
        subtitle = u'%s，气温：%s' % (data['wind'], data['temperature'])
        icon = (get_weather_icon_name(data['dayPictureUrl']), {'type': 'png'})
        weather_data = alfred.Item(title=title, subtitle=subtitle, icon=icon)
        result.append(weather_data)
    return alfred.xml(result)


def show_weather(query=''):
    alfred.write(get_weather(query))
