import argparse
import io
import sys

import sqlalchemy as sql
from nose.tools import assert_equals

from blog import parse_args, Blog


def test_parse_args():
    parsed = parse_args(['post', 'add', 'title', 'content'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='add', category=None,
        add=['title', 'content']), parsed)
    parsed = parse_args(['post', 'add', 'title', 'content', '--category',
                         'category'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='add', category='category',
        add=['title', 'content']), parsed)
    parsed = parse_args(['post', 'list', ])
    assert_equals(argparse.Namespace(
        command='post', subcommand='list', ), parsed)
    parsed = parse_args(['post', 'search', 'word'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='search', search='word'), parsed)
    parsed = parse_args(['category', 'add', 'category-name'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='add', category='category-name'), parsed)
    parsed = parse_args(['category', 'list', ])
    assert_equals(argparse.Namespace(
        command='category', subcommand='list', category=None), parsed)
    parsed = parse_args(['category', 'list', 'category-name'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='list', category='category-name'),
        parsed)
    parsed = parse_args(['category', 'assign', '2', '5'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='assign', post=2, category=5), parsed)


class TestBlog:

    def setup(self):
        self.blog = Blog(engine='sqlite://')
        self.savedstdout = sys.stdout
        sys.stdout = io.StringIO()

    def teardown(self):
        self.blog.metadata.drop_all()
        sys.stdout = self.savedstdout

    def test_post_add(self):
        self.blog.post_add('test post', 'test content')
        expected_result = [(1, 'test post', 'test content')]
        real_result = list(sql.select([self.blog.posts_table]).execute())
        assert_equals(expected_result, real_result)

    def test_post_add_category(self):
        self.blog.post_add('test post', 'test content',
                           category_name='test category')
        expected_posts = [(1, 'test post', 'test content')]
        expected_categories = [(1, 'test category',)]
        expected_categories_posts = [(1, 1, 1)]
        real_posts = list(sql.select([self.blog.posts_table]).execute())
        real_categories = \
            list(sql.select([self.blog.categories_table]).execute())
        real_categories_posts = list(
            sql.select([self.blog.categories_posts_table]).execute())
        assert_equals(expected_posts, real_posts)
        assert_equals(expected_categories, real_categories)
        assert_equals(expected_categories_posts, real_categories_posts)

    def test_post_list(self):
        self.blog.posts_table.insert().execute(
            title='test title', content='test content')
        self.blog.post_list()
        assert_equals(
            sys.stdout.getvalue().strip(), '1 | test title | test content')

    def test_post_search(self):
        self.blog.posts_table.insert().execute(
            title='test title', content='test content')
        self.blog.posts_table.insert().execute(
            title='second', content='2nd post')
        self.blog.posts_table.insert().execute(title='third', content='3rd')
        self.blog.post_search('second')
        assert_equals(sys.stdout.getvalue().strip(), '2 | second | 2nd post')

    def test_category_add(self):
        self.blog.category_add('my category')
        expected_result = [(1, 'my category')]
        real_result = list(sql.select([self.blog.categories_table]).execute())
        assert_equals(expected_result, real_result)

    def test_category_list(self):
        self.blog.categories_table.insert().execute(name='test category')
        self.blog.category_list()
        expected_result = '1 test category'
        real_result = sys.stdout.getvalue().strip()
        assert_equals(expected_result, real_result)

    def test_category_assign(self):
        self.blog.posts_table.insert().execute(
            title='test title', content='test content')
        self.blog.categories_table.insert().execute(name='test category')
        self.blog.category_assign(1, 1)
        expected_result = [(1, 1, 1)]
        real_result = list(
            sql.select([self.blog.categories_posts_table]).execute())
        assert_equals(expected_result, real_result)
        self.blog.category_assign(1, 2)
        assert_equals(sys.stdout.getvalue().strip(),
                      'post or category with given id does not exist')
