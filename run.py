import os


# if COVERAGE is set start test coverage
COV = None
if os.environ.get('COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


import sys
import click
from app import create_app, db
from app.models import User, Role, Permission, Comment, Post


app = create_app(os.getenv('APP_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post,
        Comment=Comment)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='run tests under code coverage')
def test(coverage):
    """run unit tests"""
    
    # if tests ran with coverage option, recursively restart the script and
    # set COVERAGE environment variable to true
    if coverage and not os.environ.get('COVERAGE'):
        print('restarting script ...')
        os.environ['COVERAGE'] = '1'
        args = [sys.argv[0] + '.exe'] + sys.argv[1:]
        os.execvp(sys.executable, [sys.executable] + args)

    # start tests
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    # coverage ended, display result in terminal and store it as html in /tmp folder
    if COV:
        COV.stop()
        COV.save()
        print('coverage summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print(f'HTML version: { covdir }/index.html')
        COV.erase()
