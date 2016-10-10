#!/usr/bin/env python

import requests
import sys
import json


#init vars and check params
response = ''
url = hipchatServer['serverName']
token = hipchatServer['token']
proxyUrl = hipchatServer['proxyUrl']

print dir(__builtins__)
for x in __builtins__.iterkeys() :
    print x

for x in dir() :
    print x 



def hipchat_notify(token, room, message, color='yellow', notify=False,
                   format='text', host='api.hipchat.com'):

    """Send notification to a HipChat room via API version 2

    Parameters
    ----------
    token : str
        HipChat API version 2 compatible token (room or user token)
    room: str
        Name or API ID of the room to notify
    message: str
        Message to send to room
    color: str, optional
        Background color for message, defaults to yellow
        Valid values: yellow, green, red, purple, gray, random
    notify: bool, optional
        Whether message should trigger a user notification, defaults to False
    format: str, optional
        Format of message, defaults to text
        Valid values: text, html
    host: str, optional
        Host to connect to, defaults to api.hipchat.com
    """

    if len(message) > 10000:
        raise ValueError('Message too long')
    if format not in ['text', 'html']:
        raise ValueError("Invalid message format '{0}'".format(format))
    if color not in ['yellow', 'green', 'red', 'purple', 'gray', 'random']:
        raise ValueError("Invalid color {0}".format(color))
    if not isinstance(notify, bool):
        raise TypeError("Notify must be boolean")


    url = "https://{0}/v2/room/{1}/notification".format(host, room)
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token




    description = "Xl-Release is about to start a deployment"
    release = releases_url
    card = {
        'style': "application",
        'url': "http://wians-macbook-pro-2.local:5516/static/5.0.1/img/xl-release-logo-white.svg",
        'format': "medium",
        'id': "db797a68-0aff-4ae8-83fc-2e72dbb1a707",
        'title': "XL-Release Notification",
        'description': description,
        'icon': {
            'url': "http://wians-macbook-pro-2.local:5516"
        },
            'attributes': [
                {
                    'label': "Release",
                    'value': {
                        'label': release
                        }
                },
                {
                    'label': "attribute2",
                    'value': {
                        'icon': {
                            'url': "http://bit.ly/1S9Z5dF"
                            },
                        'label': "value2",
                        'style': "lozenge-complete"
                          }
                        }
                      ]
                    }

    payload = {'message': message,
                'card' : card}
    r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    r.raise_for_status()


try:
    hipchat_notify(token, room, message)
except Exception as e:
        msg = "[ERROR] HipChat notify failed: %s" % e
        print msg
        sys.exit(1)
