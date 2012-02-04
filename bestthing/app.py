#!/usr/bin/env python
#
# Copyright 2012 Naan Labs Inc. 
#

import os
import os.path
import sys
import subprocess
import re
import time
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import json
import ConfigParser
import zmq
import pdb
import markdown
from tornado.options import define, options

define("port", default=8889, help="run on the given port", type=int)


def parseCfgFile(_path, sectionName, sectionCfg):
    config = ConfigParser.ConfigParser()
    config.read(_path)
    for k, v in config.items(sectionName):
        sectionCfg[k] = v


def splitMsg(msg):
    (x, y) = msg.split("")
    return (x, y)


class ZmqClient:

    def __init__(self, appCfg):
        host = appCfg['zmq_sever_host'].strip('"').strip("'")
        jScAdddr = appCfg['judge_sckt_port'].strip("'").strip('"')
        addScAddr = appCfg['add_concept_sckt_port'].strip("'").strip('"')
        ldrScAddr = appCfg['leaderboard_sckt_port'].strip("'").strip('"')
        self.__context = zmq.Context()
        self.__judge_sckt = self.__context.socket(zmq.REQ)
        self.__judge_sckt.connect('tcp://' + host + ':' + jScAdddr)
        self.__add_concept_sckt = self.__context.socket(zmq.REQ)
        self.__add_concept_sckt.connect('tcp://' + host + ':' + addScAddr)
        self.__leader_sckt = self.__context.socket(zmq.REQ)
        self.__leader_sckt.connect('tcp://' + host + ':' + ldrScAddr)

    def __del__(self):
        self.__judge_sckt.close()
        self.__add_concept_sckt.close()
        self.__leader_sckt.close()
        self.__context.term()

    def get_concepts_to_judge(self):
        self.__judge_sckt.send_unicode('gimme')
        message = self.__judge_sckt.recv_unicode().strip()
        if message == "No more or very less concepts to judge":
            return None
        (c1, c2) = message.split(':')
        p1 = splitMsg(c1.strip())
        p2 = splitMsg(c2.strip())
        return (('%s:%s' % (p1[0], p2[0]), p1[1]), ('%s:%s' % (p2[0],
                        p1[0]), p2[1]))

    def handle_judgement(self, c1, c2):
        self.__judge_sckt.send_unicode('%s,%s:%d' % (c1, c2, 1))
        message = self.__judge_sckt.recv_unicode()

    def get_top10_concepts(self):
        self.__leader_sckt.send_unicode('gimme')
        message = self.__leader_sckt.recv_unicode()
        top10 = message.strip().split("")
        return top10

    def submit_concept(self, concept):
        self.__add_concept_sckt.send_unicode(concept)
        self.__add_concept_sckt.recv_unicode()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def zmq_client(self):
        return self.application.zmq_client


class HomeHandler(BaseHandler):

    def get(self):
        concepts = self.zmq_client.get_concepts_to_judge()
        if concepts is None:
            self.render("done.html")
        else:
            self.render("judge.html", concepts = concepts)

    def post(self):
        (goodConceptId, badConceptId) = \
         self.get_argument('concept').strip().split(':')
        self.zmq_client.handle_judgement(goodConceptId,\
                badConceptId)
        self.redirect('/')


class AboutHandler(BaseHandler):

    def get(self):
        f = open('./about.md', 'r')
        md = f.read()
        f.close()
        html = markdown.markdown(md)
        self.render("about.html", htmlText = html)



class SubmitConceptHandler(BaseHandler):

    def get(self):
        self.render("submit_concept.html")

    def post(self):
        concept = self.get_argument('concept').strip()
        self.zmq_client.submit_concept(concept)
        self.redirect('/')


class LeaderboardHandler(BaseHandler):

    def get(self):
        top10 = self.zmq_client.get_top10_concepts()
        self.render("leaderboard.html", top10 = top10)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/leaderboard", LeaderboardHandler),
            (r"/submit", SubmitConceptHandler),
            (r"/about", AboutHandler),
        ]
        settings = dict(
            app_name=u"Best Thing Ever",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            autoescape=None,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        appCfg = {}
        parseCfgFile('./.app.cfg', 'global', appCfg)
        self.zmq_client = ZmqClient(appCfg)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

