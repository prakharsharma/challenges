#!/usr/bin/python

import zmq
import time
import ConfigParser

def parseCfgFile(_path, sectionName, sectionCfg):
    config = ConfigParser.ConfigParser()
    config.read(_path)
    for k, v in config.items(sectionName):
        sectionCfg[k] = v


appCfg = {}
parseCfgFile('./.app.cfg', 'global', appCfg)
context = zmq.Context()
keep_alive_sckt = context.socket(zmq.REQ)
keep_alive_sckt.connect('tcp://localhost:' +\
        appCfg['keep_alive_sckt_port'].strip('"').strip("'"))

while True:
    keep_alive_sckt.send_unicode('refresh')
    keep_alive_sckt.recv_unicode()
    time.sleep(2 * 60)

if __name__ == "__main__":
    pass
