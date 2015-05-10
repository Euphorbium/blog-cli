import argparse

import sqlalchemy  as sql

def main():

    parser = argparse.ArgumentParser(description='Manage your blog from command line',)
    subparsers = parser.add_subparsers(
        help='you should choose if you want to work with posts, or categories',
        dest='command')
    category_parser = subparsers.add_parser('category', help="work with categories")
    category_subparsers = category_parser.add_subparsers(help="add, list or assign a category to a post",
                                                         dest='subcommand')
    category_add = category_subparsers.add_parser('add',)
    category_assign = category_subparsers.add_parser('assign',)
    category_assign.add_argument('post', type=int)
    category_assign.add_argument('category', type=int)
    category_list = category_subparsers.add_parser('list',)
    category_list.add_argument('category', nargs='?', help='list all the posts assigned to listed categories. If no category is'
                               'specified, lists all the categories', default=None)
    category_add.add_argument('add', nargs='+')
    post_parser = subparsers.add_parser('post', help="work with posts")
    post_subparsers = post_parser.add_subparsers(help="add, list or search",  dest='subcommand')
    post_add = post_subparsers.add_parser('add',)
    post_list = post_subparsers.add_parser('list',)
    post_search = post_subparsers.add_parser('search',)
    post_search.add_argument('search', nargs=1, help='search for blog posts containing given string')
    post_add.add_argument('add', nargs=2, help="add a blog post with a given title", type=str)
    post_add.add_argument('--category', nargs="+", help="assign blog post to every listed category,"
                          "if category does not exist, this creates it first", type=str)


    args = parser.parse_args()

    print(args)
    db=sql.create_engine('sqlite:///test.db', echo=False)
    metadata = sql.MetaData(bind=db)

    posts_table=sql.Table('posts', metadata,
                          sql.Column('id', sql.Integer, primary_key=True, ),
                          sql.Column('title', sql.String(100),),
                          sql.Column('content', sql.Text,),
                          sqlite_autoincrement=True
                          )
    categories_table=sql.Table('categories', metadata,
                          sql.Column('id', sql.Integer, primary_key=True),
                          sql.Column('name', sql.String(100),),
                          sqlite_autoincrement=True
                               )
    categories_posts_table=sql.Table('categoriesPosts', metadata,
                          sql.Column('id', sql.Integer, primary_key=True),
                          sql.Column('post', sql.Integer, sql.ForeignKey('posts.id'), nullable=False),
                          sql.Column('category', sql.Integer, sql.ForeignKey('categories.id'), nullable=False),
                          sqlite_autoincrement=True
                               )
    metadata.create_all()
    conn=db.connect()

    if args.command=='post':
        if args.subcommand=='add':
            title = args.add[0]
            content = args.add[1]
            print('adding blog post with title %s' % title)
            posts_table.insert().execute(title=args.add[0], content=args.add[1])
        if args.subcommand=='list':
            posts = sql.select([posts_table]).execute()
            for post in posts:
                print(post)
        if args.subcommand=='search':
            posts = sql.select([posts_table]).where(
                               (posts_table.c.title.like('%{0}%'.format(args.search[0])))|\
                                (posts_table.c.content.like('%{0}%'.format(args.search[0])))).execute()
            for post in posts:
                print(post)
    elif args.command=='category':
        if args.subcommand=='add':
            categories_table.insert().execute(name=args.add[0],)
        elif args.subcommand=='list':
            if args.category:
                posts = sql.select(
                    [posts_table, categories_table, categories_posts_table]
                ).where(
                    (posts_table.c.id==categories_posts_table.c.post) &\
                    (categories_table.c.id==categories_posts_table.c.category) &\
                    (categories_table.c.name.like('%{0}%'.format(args.category)))\
                ).execute()
                for post in posts:
                    print(post)
            else:
                categories = sql.select([categories_table]).execute()
                for category in categories:
                    print(category)
        elif args.subcommand=='assign':
            categories_posts_table.insert().execute(post=args.post, category=args.category)


if __name__=="__main__":
    main()
