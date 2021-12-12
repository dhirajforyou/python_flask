#!/usr/bin/env python

import os
from app import create_app, db
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app=app, db=db)

if __name__ == '__main__':
    app.run()
