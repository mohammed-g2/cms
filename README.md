# Blogging engine

## Features

- basic user authentication
- create and edit blogs and comments
- followers
- user profile customization
- adminstration: edit / delete blogs, comments
- adminstration: edit accounts
- moderation: moderate user comments

#### command line:

    flask test      "run unit tests"
    options:
    --coverage      "run unit tests with code coverage"

    flask profile   "start application under code profiler"
    options:
    --log-data      "if true, profile data for each request is saved to a file in tmp/profile directory"
    --length        "number of function to include in the report"

## To Do

- better ui

#### Features

- api (partially implemented)
- like posts
- (adminstration) ban / delete users
- facebook / twitter login

#### Testing

- models unit tests
- Integration tests
- end to end tests (ui test)
- logging performance / errors
