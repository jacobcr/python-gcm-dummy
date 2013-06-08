# -*- coding: utf-8 -*-
import json
import os
from copy import copy
from optparse import OptionParser
from gevent import monkey; monkey.patch_all()
from gevent import pywsgi

results = {}

template = {
        'failure': 0,
        'canonical_ids': 0,
        'success': 0,
        'multicast_id': 6616353152392206975,
        'results': []
    }
def response_ok():
    response = copy(template)
    response['failure'] = 0
    response['success'] = 1
    response['results'].append({u'message_id': u'0:1370674827295849'})
    return response

def response_invalid():
    response = copy(template)
    response['failure'] = 1
    response['success'] = 0
    response['results'].append({u'error': u'InvalidRegistration'})
    return response

def response_update():
    response = copy(template)
    response['failure'] = 0
    response['success'] = 1
    response['canonical_ids'] = 1
    response['results'].append({u'message_id': u'0:1370674827295849', u'registration_id': 'tokenupdated'})
    return response

ops = {
    'OK': response_ok,
    'INVALID': response_invalid,
    'UPDATE': response_update
}

def handle(env, start_response):
    body =json.loads(env['wsgi.input'].read())
    regid = body['registration_ids'][0] # only one reg id is supported
    if regid in results:
        response = ops[results[regid].strip().upper()]()
    else:
        # by default response will be ok
        response = response_ok()

    start_response('200 OK', [('Content-Type', 'application/json')])
    print response
    return  [json.dumps(response)]

def main():
    parser = OptionParser()
    parser.add_option(
        "-p", "--port",
        dest="port",
        help="Server port [%default]",
        default=8081)

    parser.add_option(
        "-b", "--bind_address",
        dest="bind",
        help="Bind addreess [%default]",
        default="0.0.0.0")

    parser.add_option(
        "-r", "--results_file",
        dest="rfile",
        help="Results file [%default]",
        default="results.csv")

    (options, args) = parser.parse_args()

    # By default server outputs ok responses, but a results file could be defined to define responses.
    if os.path.exists(options.rfile):
        print 'Loaded %s file' % options.rfile
        global results
        results = dict(x.strip().split(',') for x in open(options.rfile, 'r'))


    print "Starting server on %s:%s" % (options.bind, options.port)
    pywsgi.WSGIServer((options.bind, options.port), handle).serve_forever()

if __name__ == "__main__":
    main()
