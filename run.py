import os
from app import create_app, db
from app.models import User, Role, Permission


app = create_app(os.getenv('APP_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission)


@app.context_processor
def make_context():
    return dict(Permission=Permission)


@app.cli.command()
def test():
    """run unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)