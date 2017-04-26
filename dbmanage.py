#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(repository='database_migrate', debug='False', url='sqlite:////home/mcproger/meetup-facebook-bot/app.db') #for testing on local machine
