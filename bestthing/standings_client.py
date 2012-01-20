#!/usr/bin/python

import zmq

ctxt = zmq.Context()
sckt = ctxt.socket(zmq.REQ)
sckt.connect('tcp://localhost:7777')

sckt.send('gimme')
message = sckt.recv()
print 'Current standings: %s' % message

sckt.close()
ctxt.term()

if __name__ == "__main__":
    pass

