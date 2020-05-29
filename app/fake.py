from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Post, Comment
from config import Config


def users(count=100):
    """empty tables and create fake data"""
    User.query.delete()
    fake = Faker()
    admin = User(email=Config.ADMIN,
            username='admin',
            password='123456',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date())
    db.session.add(admin)
    db.session.commit()
    
    i = 0
    while i < count:
        u = User(email=fake.email(),
            username=fake.user_name(),
            password='123456',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    """empty tables and create fake data"""
    Post.query.delete()
    fake = Faker()
    user_count = User.query.count()
    i = 0
    while i < count:
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(title=fake.word(),
            body=fake.text(),
            timestamp=fake.past_date(),
            author=u)
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def comments(per_post=10):
    fake = Faker()
    posts = Post.query.all()
    user_count = User.query.count()
    for post in posts:
        for _ in range(per_post):
            user = User.query.get(randint(1, user_count))
            comment = Comment(body=fake.text(), post=post, author=user)
            db.session.add(comment)

    db.session.commit()
