#! /usr/bin/env python3
import argparse
import sys

import sqlalchemy as sql
from sqlalchemy.exc import IntegrityError


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Manage your blog from command line', )
    subparsers = parser.add_subparsers(
        help='you should choose if you want to work with posts, or categories',
        dest='command')
    category_parser = subparsers.add_parser(
        'category', help="work with categories")
    category_subparsers = category_parser.add_subparsers(
        help="add, list or assign a category to a post", dest='subcommand')
    category_add = category_subparsers.add_parser('add', )
    category_assign = category_subparsers.add_parser('assign', )
    category_assign.add_argument('post', type=int)
    category_assign.add_argument('category', type=int)
    category_list = category_subparsers.add_parser('list', )
    category_list.add_argument(
        'category', nargs='?', help='list posts of a given category. If no '
                                    'category is specified, lists all the categories', default=None)
    category_add.add_argument('category', )
    post_parser = subparsers.add_parser('post', help="work with posts")
    post_subparsers = post_parser.add_subparsers(
        help="add, list or search", dest='subcommand')
    post_add = post_subparsers.add_parser('add', )
    post_list = post_subparsers.add_parser('list', )
    post_search = post_subparsers.add_parser('search', )
    post_search.add_argument(
        'search', help='search for blog posts containing given string')
    post_add.add_argument(
        'add', nargs=2, help="add a blog post with a given title", type=str)
    post_add.add_argument(
        '--category', help="assign blog post to a category,"
                           "if category does not exist, it will be created",
        type=str, default=None)
    return parser.parse_args(args)


class Blog:

    def __init__(self, engine='sqlite:///blog.db'):
        try:
            self.db = sql.create_engine(engine, echo=False)
        except:
            sys.stderr.write('failed to connect to a database')
            raise
        self.metadata = sql.MetaData(bind=self.db)

        def _fk_pragma_on_connect(dbapi_con, con_record):  # need to make sure sqlite has foreign keys enabled
            dbapi_con.execute('pragma foreign_keys=ON')

        sql.event.listen(self.db, 'connect', _fk_pragma_on_connect)

        self.posts_table = sql.Table(
            'posts', self.metadata,
            sql.Column(
                'id', sql.Integer, primary_key=True, ),
            sql.Column('title', sql.String(100), ),
            sql.Column('content', sql.Text, ),
            sqlite_autoincrement=True
        )
        self.categories_table = sql.Table(
            'categories', self.metadata,
            sql.Column(
                'id', sql.Integer, primary_key=True, ),
            sql.Column(
                'name', sql.String(100), unique=True),
            sqlite_autoincrement=True
        )
        self.categories_posts_table = sql.Table(
            'categoriesPosts', self.metadata,
            sql.Column(
                'id', sql.Integer,
                primary_key=True),
            sql.Column(
                'post', sql.Integer,
                sql.ForeignKey('posts.id'),
                nullable=False),
            sql.Column('category',
                       sql.Integer, sql.ForeignKey(
                    'categories.id'),
                       nullable=False),
            sqlite_autoincrement=True
        )
        self.metadata.create_all()

    def post_add(self, title, content, category_name=None):
        post_id = self.posts_table.insert().execute(
            title=title, content=content).inserted_primary_key[0]
        if category_name:
            category = sql.select([self.categories_table]).where(
                self.categories_table.c.name == category_name).execute().first()
            if category:
                self.categories_posts_table.insert().execute(
                    post=post_id, category=category.id)
            else:
                category_id = self.categories_table.insert().execute(
                    name=category_name, ).inserted_primary_key[0]
                self.categories_posts_table.insert().execute(
                    post=post_id, category=category_id)
        return post_id

    def post_list(self):
        posts = sql.select([self.posts_table]).execute()
        for post in posts:
            print(post.id, '|', post.title, '|', post.content)

    def post_search(self, search):
        posts = sql.select([self.posts_table]).where(
            (self.posts_table.c.title.like('%{0}%'.format(search))) |
            (self.posts_table.c.content.like('%{0}%'.format(search)))).execute()
        for post in posts:
            print(post.id, '|', post.title, '|', post.content)

    def category_add(self, category):
        self.categories_table.insert().execute(name=category, )

    def category_list(self, category=None):
        if category:
            posts = sql.select(
                [self.posts_table, self.categories_table,
                 self.categories_posts_table],
                use_labels=True
            ).where(
                (self.posts_table.c.id == self.categories_posts_table.c.post) &
                (self.categories_table.c.id ==
                 self.categories_posts_table.c.category) &
                (self.categories_table.c.name == category)
            ).execute()
            if posts:
                for post in posts:
                    print(
                        post.posts_id, '|', post.posts_title, '|',
                        post.posts_content)
            else:
                print('No posts found')
        else:
            categories = sql.select([self.categories_table]).execute()
            for category in categories:
                print(category.id, category.name)

    def category_assign(self, post, category):
        try:
            self.categories_posts_table.insert().execute(
                post=post, category=category)
        except IntegrityError:
            print('post or category with given id does not exist')


def main():
    args = parse_args(sys.argv[1:])
    blog = Blog()
    if args.command == 'post':
        if args.subcommand == 'add':
            title = args.add[0]
            content = args.add[1]
            blog.post_add(title, content, category_name=args.category)
        if args.subcommand == 'list':
            blog.post_list()
        if args.subcommand == 'search':
            blog.post_search(args.search)
    elif args.command == 'category':
        if args.subcommand == 'add':
            blog.category_add(args.category)
        elif args.subcommand == 'list':
            blog.category_list(args.category)
        elif args.subcommand == 'assign':
            blog.category_assign(args.post, args.category)


if __name__ == "__main__":
    main()
