import argparse
from blog import parse_args
from nose.tools import assert_equals

def test_parse_args():
    parsed = parse_args(['post', 'add', 'title', 'content'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='add', category=None, add=['title', 'content']), parsed)
    parsed = parse_args(['post', 'add', 'title', 'content', '--category', 'category'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='add', category='category', add=['title', 'content']), parsed)
    parsed = parse_args(['post', 'list',])
    assert_equals(argparse.Namespace(
        command='post', subcommand='list',), parsed)
    parsed = parse_args(['post', 'search', 'word'])
    assert_equals(argparse.Namespace(
        command='post', subcommand='search', search='word'), parsed)
    parsed = parse_args(['category', 'add', 'category-name'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='add', category='category-name'), parsed)
    parsed = parse_args(['category', 'list',])
    assert_equals(argparse.Namespace(
        command='category', subcommand='list', category=None), parsed)
    parsed = parse_args(['category', 'list', 'category-name'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='list', category='category-name'), parsed)
    parsed = parse_args(['category', 'assign', '2', '5'])
    assert_equals(argparse.Namespace(
        command='category', subcommand='assign', post=2, category=5), parsed)



def test_post_add():
    pass

def test_post_add_category():
    pass

def test_post_list():
    pass

def test_post_search():
    pass

def test_category_add():
    pass

def test_category_assign():
    pass
