#!/usr/bin/env python3
"""Copyright © 2016 Arti Zirk <arti.zirk@gmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.
"""

from time import sleep, strftime, gmtime
from pprint import pprint
import threading
import json
import urllib.request

url = "http://127.0.0.1/api/pub/beerpong"

def post(ev, data):
    data = json.dumps(data).encode("utf8")
    req = urllib.request.Request(url, data=data, headers={'content-type': 'application/json', 'X-EventSource-Event': ev})
    with urllib.request.urlopen(req) as resp:
        code = resp.getcode()
        if code >= 200 and code < 300:
            pass
        else:
            print("error code", code)


class Beerpong(threading.Thread):
    left_running = False
    right_running = False
    match_time = 60*10
    left = match_time
    right = match_time
    left_show = True
    right_show = True

    def run(self):
        while True:
            if self.left_show:
                post("left-time", {"time":strftime("%M:%S", gmtime(self.left))})
            else:
                post("left-time", {"time":"&nbsp;"})
            if self.right_show:
                post("right-time", {"time":strftime("%M:%S", gmtime(self.right))})
            else:
                post("right-time", {"time":"&nbsp;"})
            if self.left_running:
                self.left -= 1
            if self.right_running:
                self.right -= 1
            if self.left == 0:
                self.left_running = False
                if self.left_show:
                    self.left_show = False
                else:
                    self.left_show = True
            if self.right == 0:
                self.right_running = False
                if self.right_show:
                    self.right_show = False
                else:
                    self.right_show = True
            sleep(1)


beerpong = Beerpong(name="beerpong", daemon=True)
beerpong.start()

def application(env, start_response):

    if env["REQUEST_METHOD"] == "POST":
        path = env["PATH_INFO"]
        if path == "/left/start":
            beerpong.left_running = True
            beerpong.left_show = True
            start_response("204 OK", [])
            return []
        elif path == "/left/pause":
            beerpong.left_running = False
            beerpong.left_show = True
            start_response("204 OK", [])
            return []
        elif path == "/left/reset":
            beerpong.left = beerpong.match_time
            beerpong.left_running = False
            beerpong.left_show = True
            start_response("204 OK", [])
            return []


        elif path == "/right/start":
            beerpong.right_running = True
            beerpong.right_show = True
            start_response("204 OK", [])
            return []
        elif path == "/right/pause":
            beerpong.right_running = False
            beerpong.right_show = True
            start_response("204 OK", [])
            return []
        elif path == "/right/reset":
            beerpong.right = beerpong.match_time
            beerpong.right_show = True
            beerpong.right_running = False
            start_response("204 OK", [])
            return []
        else:
            start_response("404 Not Found", [])
            return []
    else:
        start_response("404 Not Found", [])
        return []


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    httpd = make_server('127.0.0.1', 8080, application)
    print("Serving on http://127.0.0.1:8080/")
    httpd.serve_forever()
