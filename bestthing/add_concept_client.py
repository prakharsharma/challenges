#!/usr/bin/python

import zmq

ctxt = zmq.Context()
sckt = ctxt.socket(zmq.REQ)
sckt.connect('tcp://localhost:5555')
while True:
    c = raw_input('continue(y/n): ')
    c = (c != 'y' and [False] or [True])[0]
    if c == False:
        break
    sckt.send(raw_input('message: '))
    message = sckt.recv()
    if message == 'added':
        print 'Concept added.'

sckt.close()
ctxt.term()

if __name__ == "__main__":
    pass

