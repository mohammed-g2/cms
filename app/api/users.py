from . import api


@api.route('/user/<int:id>')
def get_user(id):
    pass


@api.route('/user/<int:id>/posts')
def get_user_posts(id):
    pass


@api.route('/user/<int:id>/followed/posts')
def get_user_followed_posts(id):
    pass
