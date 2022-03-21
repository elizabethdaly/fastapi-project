# from urllib import response
import pytest
from app import schemas
from tests.conftest import authorized_client, test_posts, test_user

# test that an authorized user can get all posts
def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    # validation
    def validate(post):
        return schemas.PostOut(**post)
    posts_map = map(validate, res.json())
    posts_list = list(posts_map)

    assert len(res.json()) == len(test_posts)
    assert res.status_code == 201 # correct value is 200

    # next won't work as order of posts returned is not by id (always seems to be 2)
    # print(posts_list[0].Post.id)
    # do assert if you order posts first or something
    # assert posts_list[0].Post.id == test_posts[0]

# test that an unauthorized user CAN'T get all posts
def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

# test that an unauthorized user can't get post by id
def test_unauthorized_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}") # sqlachemy model to python dict
    assert res.status_code == 401

# test that an authorized user cannot get a post with id that does not exist
def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/999999")
    res.status_code == 404

# test that an authorized user can get a valid post
def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json()) # pydantic model, see schemas.py
    # check any property of the post
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title

@pytest.mark.parametrize("title, content, published", [ 
    ("new content", "new title", True),
    ("favourite pizza", "Veggie", False),
    ("favourite colour", "blue", True)
])
# test create post with authorized user
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("/posts/", json = ({"title": title, "content": content, 
        "published": published}))
    
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

# test that default published value of created post = true
def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post("/posts/", json = ({"title": "arb_title", "content": "arb_content"}))

    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "arb_title"
    assert created_post.content == "arb_content"
    assert created_post.published == True # should be default = true as we didn't set it
    assert created_post.owner_id == test_user['id']

# test that unauthorized user cannot create a post
def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post("/posts/", json = ({"title": "arb_title", "content": "arb_content"}))
    assert res.status_code == 401

# test that unauthorized user cannot delete a post by id
def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f'/posts/{test_posts[0].id}')
    assert res.status_code == 401

# test that an authorized user can delete a post
def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f'/posts/{test_posts[0].id}')
    assert res.status_code == 204

# test that uthorized user cannot delete non existant post
def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f'/posts/800000000000')
    assert res.status_code == 404

# test that a user (test_user) can't delete someone else's (test_user2) post
def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f'/posts/{test_posts[3].id}')
    assert res.status_code == 403

# test that auth user can update a post (their own one)
def test_update_post(authorized_client, test_user, test_posts):
    # provide the data for the update
    data = {"title": "updated title", "content": "updated content", "id": test_posts[0].id}
    # send new data in body of request
    res = authorized_client.put(f'/posts/{test_posts[0].id}', json=data)
    # validate the data against our Post schema
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

# test that auth user cannot update another user's post
def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    # provide the data for the update
    data = {"title": "updated title", "content": "updated content", "id": test_posts[3].id}
    res = authorized_client.put(f'/posts/{test_posts[3].id}', json=data)
    assert res.status_code == 403

# test that unauthorized user can't update a post
def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(f'/posts/{test_posts[0].id}')
    assert res.status_code == 401

# test that authorized user can't update a post that doesn't exist
def test_update_post_non_exist(authorized_client, test_user, test_posts):
    # need to prived data to avoid validation errors
    data = {"title": "updated title", "content": "updated content", "id": test_posts[3].id}
    res = authorized_client.put(f'/posts/800000000000', json=data)
    assert res.status_code == 404