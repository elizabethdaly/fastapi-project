
# what pydantic expects before joins in posts.py get_posts function
{
        "title": "checking token var",
        "content": "relatively",
        "published": true,
        "id": 9,
        "created_at": "2022-01-08T19:04:39.387111+00:00",
        "owner_id": 18,
        "owner": {
            "id": 18,
            "email": "liz@gmail.com",
            "created_at": "2022-01-08T18:36:41.881297+00:00"
        }
    },


# what is returned after the joins
{
        "Post": {
            "published": false,
            "title": "more posts",
            "id": 19,
            "owner_id": 18,
            "content": "Check out these ones",
            "created_at": "2022-01-09T15:47:35.541577+00:00"
        },
        "votes": 1
    },