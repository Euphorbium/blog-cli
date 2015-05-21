[![Build Status](https://travis-ci.org/Euphorbium/blog-cli.svg?branch=master)](https://travis-ci.org/Euphorbium/blog-cli)
___

# Requirements:
1. sqlalchemy
2. nose (if you want to use tests)

# Example usage:
To write a new blog post:

`./blog.py post add "post title" "post content"`

This gives no output, but the post is added to the database.
You can also assign a category to a post:

`./blog.py post add "post title" "post content" --category "my category"`

If the category does not exist, it gets created.

`./blog.py post list` will list all the posts in a following format: `post_id | posts_name | post_content`

`./blog.py post search "search_term"` will list only those posts that match the search term in title or content.

`./blog.py category add "my category"` will add a new category

`./blog.py category list` will list all the categories. If you specify a category (`./blog.py category list "my category"`) it will list all the posts assigned to that category.

`./blog.py category assign 1 2` will asign a post with an id 1 to a category with an id 2

`--help` will give help message for any command












