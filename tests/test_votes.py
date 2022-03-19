import pytest
from app import models

@pytest.fixture()
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()

# test that an authorized user can vote for ANY post
# strictly, should not be able to vote for own post, but hey
def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert res.status_code == 201

# test that auth user can't like a post twice
# for this we need to set up a post that already has a vote
def test_vote_twice_post(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert res.status_code == 409

# test that we can delete a vote
def test_delete_vote(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 201

# test deleting a vote for a post we never liked in the first place
# so we don't have the test vote
def test_delete_vote_not_liked(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 404

# test that we can't vote on a post that doesn't exist
def test_vote_post_non_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": 80000, "dir": 1})
    assert res.status_code == 404

# test that non authenticated user can't vote
def test_vote_unauthorized_user(client, test_posts):
    res = client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert res.status_code == 401
