from flask import jsonify, g, request, url_for, current_app
from app import db
from app.models import Post, Permission
from .decorators import permission_required
from .errors import forbidden
from . import api


@api.route('/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = url_for('api.get_posts', page=page-1, _external=True) if pagination.has_prev else None
    next = url_for('api.get_posts', page=page-1, _external=True) if pagination.has_next else None
    first_page = url_for('api.get_posts', page=1, _external=True)
    last_page = url_for('api.get_posts', page=pagination.pages, _external=True)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'first_page': first_page,
        'last_page': last_page,
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })


@api.route('/post/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/post', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    """create post, return created post and url for the created post"""
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return (
        jsonify(post.to_json()), 
        201, 
        {'location': url_for('api.get_post', id=post.id, _external=True)}
    )


@api.route('/post/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden('permission required')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route('/post/<int:id>/comments')
def get_post_comments(id):
    pass
