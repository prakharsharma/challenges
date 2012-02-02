#!/usr/bin/python

import zmq

ctxt = zmq.Context()
sckt = ctxt.socket(zmq.REQ)
sckt.connect('tcp://localhost:6666')
while True:
    c = raw_input('continue(y/n): ')
    c = (c != 'y' and [False] or [True])[0]
    if c == False:
        break
    sckt.send('gimme')
    message = sckt.recv()
    print 'Received %s from server' % (message, )
    if message == "No more or very less concepts to judge":
        continue
    judge = raw_input('Judgment (1 if 1st is better, else 2): ')
    message = message + ':' + judge
    sckt.send(message)
    message = sckt.recv()

sckt.close()
ctxt.term()

if __name__ == "__main__":
    pass

