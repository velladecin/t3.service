#!/usr/bin/python
import json, urllib2
import sys
import base64
from pprint import pprint
# T3
import Utils

class T3web:

    __WEBHOST = {"Mel": "j2.mel", "Syd": "j2.syd"} # ..bit ugly as it depends on definitions in Utils
    __WEBROOT = "t3web"
    __WEBPORT = 8181

    __ACTION = {
        # action name       location name

        # BCC related
        "getbcc":           "bcc",
        "getcmts":          "bcc",
        "getbccstatus":     "bcc",

        # CM related (collector)
        "getmac":           "col",
        "getip":            "col",
        "getcmcount":       "col",

        # FW related (collector)
        "getfwcount":       "col",
        "getfwcmtsmac":     "col"
    }

    def __init__(self, host=None, port=None, root=None):
        self.webhost = host
        self.webport = port
        self.webroot = root

        if not self.webhost:
            try:
                l = (Utils.getDomsSite("local"))[0]
                o = (Utils.getDomsSite("other"))[0]

                wbh = [ self.__WEBHOST[l], self.__WEBHOST[o] ]
            except KeyError as e:
                print e.args
                sys.exit(2)

            self.webhost = wbh

        if not isinstance(self.webhost, list): # given a single host via __init__
            self.webhost = [ self.webhost ]

        if not self.webport:
            self.webport = self.__WEBPORT

        if not isinstance(self.webport, int):
            print "Webport must be an integer, not %s.." % type(self.webport)
            sys.exit(2)

        if not self.webroot:
            self.webroot = self.__WEBROOT


    #
    # Meth(ods)

    def httpRequest(self, uri, val=None):
        jsondata = None

        try:
            uri = "%s/%s" % (self.__ACTION[uri], uri)
        except KeyError as e:
            print "Baad key '%s' (for __ACTION)" % e.args
            return {}

        err = []
        maxhostcount = len(self.webhost) - 1

        for hostcount, host in enumerate(self.webhost):
            url = "http://%s:%d/%s/%s" % (host, self.webport, self.webroot, uri)
            if val:
                url = "%s/%s" % (url, val)

            #print "URL: %s" % url

            try:
                fp = urllib2.urlopen(url, None, 4)
                code = fp.getcode()

                # we like 200+
                if code >= 200 and code <= 299:
                    jsondata = json.load(fp)
                    break

                raise HttpBadResponse("Uri '%s' returned HTTP(%d)" % (uri, code))
            except urllib2.URLError, e:
                # collect error
                err.append("%s: %s" % (host, str(e)))

                if hostcount < maxhostcount: # try another server
                    continue

                # requests to all servers failed
                print "Could not process request - %s" % ' / '.join(err)
                sys.exit(3)

        if not jsondata:
            print "No JSON data received.."
            sys.exit(4)

        return jsondata

    #
    # Privates


class HttpBadResponse(urllib2.URLError):
    pass
