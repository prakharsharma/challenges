# bestthing
This emulates the project at [bestthing.info](http://bestthing.info/)

# Requirements
- The implementation uses ZeroMQ (>= 2.1)
- Tornado web server (tested with 2.2)
- MySQL server (tested with ver 5.x)

# Running
1. Copy app.cfg to .app.cfg. Fix the ports and other end point details in
the copied file
file to .app.cfg
1. Start MySQL server
1. Start tonardo application: python app.py
1. Hit [link](http://localhost:8889/)

# Description
- app.py is a very thin proxy layer, that just brokers request/response
to/from the actual 0MQ server (bestthing_info.py)
- bestthing_info.py is the 0MQ server
- concept.py has the brains of the application
