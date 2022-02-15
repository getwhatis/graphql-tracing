import beeline
from ariadne import QueryType

from app.models import Post, Comment, query_post_v2, query_post_v3, Author

type_defs = """
    type Query {
        Post(post_input: PostInput!): Post!
        PostV2(post_input: PostInput!): Post!
        PostV3(post_input: PostInput!): Post!
    }
    
    input PostInput {
        id: Int!
    }
    
    type Post {
        id: Int!
        name: String!
        content: String
        comments: [Comment!]!
        created_at_date: String!
        created_at_time: String!
        author_name: String!
    }
    
    type Comment {
        id: Int!
        content: String!
        author: Author!
        created_at_date: String!
        updated_at_date: String!
        likes: Int!
        post: Post!
    }
    
    type Author {
        id: Int!
        name: String!
    }
"""

query = QueryType()


@query.field("Post")
def resolve_posts(_, info, post_input=None):
    post_input = post_input or {}

    if "id" in post_input:
        return Post.query.filter(Post.id == post_input["id"]).first()
    return Post.query.first()


@query.field("PostV2")
def resolve_post_v2(_, info, post_input):
    return query_post_v2(post_id=post_input["id"])


@query.field("PostV3")
def resolve_post_v3(_, info, post_input):
    rows = query_post_v3(post_id=post_input["id"])
    with beeline.tracer(name="posts_to_gql_response"):
        comments = [
            {
                "id": row[Comment.id],
                "author": {
                    "id": row[Author.id],
                    "name": row[Author.name],
                },
            }
            for row in rows
        ]
    return {
        "id": post_input["id"],
        "comments": comments,
    }
