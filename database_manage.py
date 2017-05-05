#!/usr/bin/env python
from migrate.versioning.shell import main
import os

if __name__ == '__main__':
    main(repository='database_migrate', debug='False', url=os.environ['DATABASE_URL'])