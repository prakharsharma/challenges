#!/usr/bin/python

import sys
import zmq
from concept import Concept

Concept.setup('./.app.cfg')

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


context = zmq.Context()
#
add_concept_sckt = context.socket(zmq.REP)
add_concept_sckt.bind('tcp://*:5555')

judge_concepts_sckt = context.socket(zmq.REP)
judge_concepts_sckt.bind('tcp://*:6666')

get_standings_sckt = context.socket(zmq.REP)
get_standings_sckt.bind('tcp://*:7777')

poller = zmq.Poller()
poller.register(add_concept_sckt, zmq.POLLIN)
poller.register(judge_concepts_sckt, zmq.POLLIN)
poller.register(get_standings_sckt, zmq.POLLIN)

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
        

if __name__ == "__main__":
    pass

