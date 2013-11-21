#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
#
# Copyright 2013 Telefonica Digital. All rights reserved.
#
# Authors:
#    Antonio Robres < arobres@tid.es> - 2013
#

from bottle import run, post, request, error, route
import ujson
from optparse import OptionParser
from collections import deque

response_template = {'failure': 0,
                     'canonical_ids': 0,
                     'success': 0,
                     'multicast_id': 6616353152392206975,
                     'results': []
                     }
responses_saved = deque()
requests_handled = deque()


@error(404)
def error404(error):

    return 'Nothing here, sorry'


@post("/")
def return_response():
    '''
    Response with a GCM response mocked. If there are saved responses in the dict "responses_saved", send the first
     response and deletes it. If there isn't responses saved before, send a GCM response with all the receivers as
     success.
    :return: json body with response saved or with all the receivers success.
    '''
    data = request.body.readline()
    body_received = ujson.loads(data)
    requests_handled.append(body_received)
    response = response_template

    if not responses_saved:
        response['success'] = len(body_received['registration_ids'])
        for x in range(len(body_received['registration_ids'])):
            response['results'].append(({u'message_id': u'0:1370674827295849'}))
    else:
        response = responses_saved.popleft()

    return ujson.dumps(response)


@post("/save_response")
def save_response():
    '''
    Store the body provided in a dict to be used later.
    :return: 200 OK
    '''
    data = request.body.readline()
    body_received = ujson.loads(data)
    responses_saved.append(body_received)
    return 'OK'

@route("/reset_responses")
def reset_responses():
    responses_saved.clear()
    return 'Responses deleted'

@route("/reset_stats")
def reset_stats():

    requests_handled.clear()
    return 'Stats reset'

@route("/stats")
def stats():
    body = {'num_requests': len(requests_handled),
            'requests': list(requests_handled)}
    return ujson.dumps(body)


def main():

    parser = OptionParser()
    parser.add_option(
        "-p", "--port",
        dest="port",
        help="Server port [%default]",
        default=8082)

    parser.add_option(
        "-b", "--bind_address",
        dest="bind",
        help="Bind addreess [%default]",
        default="0.0.0.0")

    (options, args) = parser.parse_args()

    print "Starting server on %s:%s" % (options.bind, int(options.port))
    run(host=options.bind, port=options.port, debug=True)


if __name__ == "__main__":
    main()
