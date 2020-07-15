import os

# if COVERAGE is set start test coverage
COV = None
if os.environ.get('COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


import sys
import click
from flask_migrate import upgrade
from app import create_app, db
from app.models import User, Role, Permission, Comment, Post


app = create_app(os.getenv('APP_CONFIG') or 'default')
basedir = os.path.abspath(os.path.dirname(__file__))


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
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print(f'HTML version: { covdir }/index.html')
        COV.erase()


@app.cli.command()
@click.option('--length', default=5, help='number of function to include in the profiler report')
@click.option('--log-data', default='true', help='if true, profile data for each request is saved to a file')
def profile(length, log_data):
    """start application under code profiler"""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    
    # make it possible to call app.run() from command line
    os.environ['FLASK_RUN_FROM_CLI'] = 'false'

    profile_dir = os.path.join(basedir, 'tmp', 'profile')

    if log_data == 'true':
        try:
            os.makedirs(profile_dir)
        except:
            pass
    else:
        profile_dir = None

    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run(debug=False)


@app.cli.command()
def deploy():
    """run deployment tasks"""
    print('migrate database to the latest version...')
    upgrade()
    print('create or update user roles...')
    Role.insert_roles()
