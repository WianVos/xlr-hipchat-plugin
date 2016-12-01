#!/usr/bin/env python

import requests
import sys
import json
import time
import pprint


#init vars and check params
serverName = hipchatServer['serverName']
token = hipchatServer['token']
proxyUrl = hipchatServer['proxyUrl']

notify=False
color = 'green'
if urgent == True :
    color = 'red'
    notify= True

latest_messages = {}

releaseId = release.getId()
releaseTitle = release.getTitle()

label = releaseId.split('/')[1]

def debug_print_response(response):
    print "Response Headers"
    print r.headers

    print "Response Body"
    print r.text


def hipchat_notify(token, room, message, label, color='yellow', notify=False,
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

    message = "Xlr :: %s :: %s (help available)" % (label, message)

    if len(message) > 10000:
        raise ValueError('Message too long')
    if format not in ['text', 'html']:
        raise ValueError("Invalid message format '{0}'".format(format))
    if color not in ['yellow', 'green', 'red', 'purple', 'gray', 'random']:
        raise ValueError("Invalid color {0}".format(color))
    if not isinstance(notify, bool):
        raise TypeError("Notify must be boolean")

    for ro in room.split(';'):
        url = "https://{0}/v2/room/{1}/notification".format(host, ro)
        headers = {'Content-type': 'application/json'}
        headers['Authorization'] = "Bearer " + token
        payload = {
            'message': message,
            'notify': notify,
            'message_format': format,
            'color': color
        }
        r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

        if $debug == True :
            debug_print_response(r)

        r.raise_for_status()

        latest_messages[ro] = hipchat_get_last_message_id(token, ro, host=host)

def hipchat_poll_for_ack(token, rooms, user, label, positive, negative, hold, interval=10,timeout=0, host='api.hipchat.com'):

    timeout_counter = 0

    while True:

        messages = []
        messages_to_user = []
        # get all recent messages from the rooms we are eyeballing
        for r in rooms.split(';'):
            messages = messages + hipchat_get_recent_history_for_room(token, r, host=host)

        # loop over the collected messages for messages adressed to this user


        for m in messages:
            mentions = get_mention_name_from_msg(m, mtype='mentions')
            if mentions != False:
                if user in mentions:
                    print "message found for user: %s" % user
                    messages_to_user.append(m)


        for m in messages_to_user:
            print m
            if label in m['message'] :


                for a in positive.split(';'):
                    if a in m['message']:
                        print "{0}:acknowledged by {1}".format(label, m['from']['name'])
                        hipchat_notify(token, rooms, "release message acknowledged by %s" % m['from']['name'], label, color="green", host=host)
                        return "Ack"

                for a in negative.split(';'):
                    if a in m['message']:
                        print "{0}:Denied by {1}".format(label, m['from']['name'])
                        hipchat_notify(token, rooms, "release message Denied by %s" % m['from']['name'], label, color="red", host=host)
                        return "Denied"

                for a in hold.split(';'):
                    if a in m['message']:
                        print "{0}:Time period extended by {1}".format(label, m['from']['name'])
                        hipchat_notify(token, rooms, "release message timeout period extended by %s" % m['from']['name'], label, color="yellow", host=host)
                        timeout_counter = 0

            elif 'help' in m['message']:

                me = """possible commands:
                        acknowledged: %s
                        Deny: %s
                        Hold: %s""" % (positive.replace(';', ' '), str(negative).replace(';', ' '), str(hold).replace(';', ' '))

                hipchat_notify(token, room, me, label, color="yellow", host=host)

        time.sleep(interval)
        timeout_counter += interval

        if timeout != 0 :
            if timeout_counter > timeout:

                return "TO"



def hipchat_get_recent_history_for_room(token, room, host='api.hipchat.com'):

    if latest_messages.has_key(room):
        latest_id = str(latest_messages[room])
        url = "https://{0}/v2/room/{1}/history/latest?not-before={2}".format(host, room, latest_id)
    else:
        url = "https://{0}/v2/room/{1}/history/latest".format(host, room)

    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token

    latest_messages[room] = hipchat_get_last_message_id(token, room, host=host)

    try:
        # print "executing request %s" % url
        r = requests.get(url, headers=headers, verify=False)
        if debug == True:
            debug_print_response(r)
        r.raise_for_status()
        messages = json.loads(r.text)
    except Exception:
            print "unable to decode information provided by %s" % url
            sys.exit(2)
    except JSONDecodeError:
            print "unable to decode output, not json formatted"
            sys.exit(2)

    return messages['items']

def hipchat_get_last_message_id(token, room, host='api.hipchat.com'):

    time.sleep(1)
    url = "https://{0}/v2/room/{1}/history/latest?max-results=1".format(host, room)
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token

    try:
        # print "executing request %s" % url
        r = requests.get(url, headers=headers, verify=False)
        if debug == True:
            debug_print_response(r)
        r.raise_for_status()
        message = json.loads(str(r.text))
    except Exception:

            print "unable to decode information provided by %s" % url
            sys.exit(2)
    except JSONDecodeError:
            print "unable to decode output, not json formatted"
            sys.exit(2)

    return message['items'][0]['id']

def get_mention_name_from_msg(msg, mtype='from'):

    nameLst = []
    if msg.has_key(mtype):
        if isinstance(msg[mtype], list):
            for x in msg[mtype]:
                nameLst.append(str(x['mention_name']))
            return nameLst
        elif isinstance(msg[mtype], dict):
            nameLst.append(str(msg[mtype]['mention_name']))
            return nameLst
        else:
            print "unable to get %s name from msg" % mtype
            return nameLst

    return nameLst

# actual script


try:
    hipchat_notify(token, room, message,label, color, host=serverName, notify=notify)
    answer = hipchat_poll_for_ack(token, room, user, label, command_positive, command_negative, command_hold, timeout=timeout, host=serverName, interval=checkInterval)
    if answer == "Ack" :
        sys.exit(0)
    elif answer == "Denied" :
        sys.exit(1)
    elif continueOnTimeout == False :
        sys.exit(2)
    else:
        sys.exit(0)

except Exception as e:
        msg = "[ERROR] HipChat notify failed: %s" % e
        print msg
        sys.exit(1)

sys.exit(0)
