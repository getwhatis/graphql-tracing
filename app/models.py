from sqlalchemy import Column, Integer, DateTime, String, ForeignKey

from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    scoped_session,
    joinedload,
)
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/graphql_tracing")
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=True)
    created_at_date = Column(DateTime, nullable=False, server_default="now()")
    updated_at_date = Column(DateTime, nullable=False, server_default="now()")
    author_name = Column(String, nullable=False)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    created_at_date = Column(DateTime, nullable=False, server_default="now()")
    updated_at_date = Column(DateTime, nullable=False, server_default="now()")
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    author = relationship("Author", backref="comments")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post = relationship("Post", backref="comments")
    likes = Column(Integer, nullable=False, server_default="0")


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


def query_post_v2(post_id: int):
    return (
        Post.query.filter(Post.id == post_id)
        .options(joinedload(Post.comments).joinedload(Comment.author))
        .first()
    )


def query_post_v3(post_id: int):
    # return (
    #     Post.query.filter(Post.id == 1)
    #     .join(Comment, Author)
    #     .with_entities(Post.id, Comment.id, Author.id, Author.name)
    # ).all()
    return (
        db_session.query(Post.id, Comment.id, Author.id, Author.name)
        .filter(Post.id == post_id)
        .join(Post.comments, Comment.author)
    ).all()


def seed(num_comments=None):
    num_comments = num_comments or 2000
    p = Post(
        name=f"Post",
        content=f"Content",
        author_name=f"Author",
    )
    db_session.add(p)
    for i in range(num_comments):
        author = Author(name=f"Author {i}")
        c = Comment(
            post=p,
            content=f"Comment {i}",
            author=author,
        )
        db_session.add_all([c, author])

    db_session.commit()
