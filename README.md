# Social App

check the project here: https://social-9.herokuapp.com/

## Features

- basic user authentication
- create and edit blogs and comments
- followers
- user profile customization
- adminstration: edit / delete blogs, comments
- adminstration: edit accounts
- moderation: moderate user comments

## How to run
first create virtual environment and install requirements

    python -m venv venv
    source venv/bin/activate (on windows venv\Scripts\activate)
    pip install -r requirements.txt

rename .env-example to .env
edit .env file, important configurations (must be set):

    FLASK_ENV
    APP_CONFIG
    SECRET_KEY

if no database url provided the app will use sqlite, then run the following commands:

    flask db migrate
    flask db upgrade
    flask deploy

finally

    flask run

#### testing
make sure to have chrome driver in the top level of the project to run selenium tests

#### command line:

    flask test      "run unit tests"
    options:
    --coverage      "run unit tests with code coverage"

    flask profile   "start application under code profiler"
    options:
    --log-data      "if true, profile data for each request is saved to a file in tmp/profile directory"
    --length        "number of function to include in the report"

    flask deploy    "run deployment tasks"

## To Do

#### Features

- api (partially implemented)
- like posts
- (adminstration) ban / delete users
- facebook / twitter login

#### Testing

- models unit tests
- Integration tests
- end to end tests (ui test)
