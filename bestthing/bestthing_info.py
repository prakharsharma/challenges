#!/usr/bin/python

import sys
import zmq
import ConfigParser
from concept import Concept


Concept.setup('./.app.cfg')


def parseCfgFile(_path, sectionName, sectionCfg):
    config = ConfigParser.ConfigParser()
    config.read(_path)
    for k, v in config.items(sectionName):
        sectionCfg[k] = v


def add_concept(message):
    print "message = %s" % str(message)
    Concept.add_concept(message)


def judge_concepts(message):
    print "message = %s" % str(message)
    if message == 'gimme':
        return Concept.get_concepts_to_judge()
    else:
        (concepts, decision) = message.strip().split(':')
        (c1, c2) = concepts.strip().split(',')
        Concept.handle_judgment(c1, c2, decision)
        return ('okay', None)


def get_standings_handler(message):
    return Concept.top_10_concepts()


def keep_alive_handler():
    Concept.keep_db_conn_alive()


appCfg = {}
parseCfgFile('./.app.cfg', 'global', appCfg)
context = zmq.Context()
#
add_concept_sckt = context.socket(zmq.REP)
add_concept_sckt.bind('tcp://*:' +\
        appCfg['add_concept_sckt_port'].strip('"').strip("'"))

judge_concepts_sckt = context.socket(zmq.REP)
judge_concepts_sckt.bind('tcp://*:' +\
        appCfg['judge_sckt_port'].strip('"').strip("'"))

get_standings_sckt = context.socket(zmq.REP)
get_standings_sckt.bind('tcp://*:' +\
        appCfg['leaderboard_sckt_port'].strip('"').strip("'"))

keep_alive_sckt = context.socket(zmq.REP)
keep_alive_sckt.bind('tcp://*:' +\
        appCfg['keep_alive_sckt_port'].strip('"').strip("'"))

poller = zmq.Poller()
poller.register(add_concept_sckt, zmq.POLLIN)
poller.register(judge_concepts_sckt, zmq.POLLIN)
poller.register(get_standings_sckt, zmq.POLLIN)
poller.register(keep_alive_sckt, zmq.POLLIN)

while True:
    socks = dict(poller.poll())
    if add_concept_sckt in socks and socks[add_concept_sckt] == zmq.POLLIN:
        message = add_concept_sckt.recv_unicode()
        add_concept(message)
        add_concept_sckt.send_unicode('added')
    if judge_concepts_sckt in socks and socks[judge_concepts_sckt] == zmq.POLLIN:
        message = judge_concepts_sckt.recv_unicode()
        (c1, c2) = judge_concepts(message)
        if c1 is None:
            judge_concepts_sckt.send_unicode('No more or very less concepts to judge')
        else:
            if c1 == 'okay':
                judge_concepts_sckt.send_unicode('okay')
            else:
                judge_concepts_sckt.send_unicode('%s:%s' % ("".join(c1),\
                            "".join(c2)))
    if get_standings_sckt in socks and socks[get_standings_sckt] == zmq.POLLIN:
        message = get_standings_sckt.recv_unicode()
        standings = get_standings_handler(message)
        get_standings_sckt.send_unicode("".join(standings))
    if keep_alive_sckt in socks and socks[keep_alive_sckt] == zmq.POLLIN:
        message = keep_alive_sckt.recv_unicode()
        keep_alive_handler()
        keep_alive_sckt.send_unicode('okay')
        

if __name__ == "__main__":
    pass

