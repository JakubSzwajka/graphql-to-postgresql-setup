

import email
from typing import List
from attr import has
import strawberry
from sqlalchemy.orm import sessionmaker
from database import SessionLocal
from fastapi import Depends, FastAPI
import models 
from strawberry.asgi import GraphQL
from sqlalchemy.orm import Session
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

# strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()

# db = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @strawberry_sqlalchemy_mapper.type(models.Item)
# class Item:
#     pass

# @strawberry_sqlalchemy_mapper.type(models.User)
# class User:
#     pass 

@strawberry.type
class User:
    name: str 
    email: str
    hashed_password: str
    is_active: bool

# def get_users():
#     return [
#         User(
#             name='John',
#             email='superjohn@example.com',
#             hashed_password='abcdefgh',
#             is_active=True
#         ),
#     ]

def get_users():
    db = SessionLocal()
    users = db.query(models.User).all( )
    db.close()

    return [
        User(
            name=user.name,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active
        )
        for user in users
    ]

def add_user(name, email, hashed_password, is_active):
    db = SessionLocal()
    db.add(models.User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active
    ))
    db.commit()
    db.close()

    return User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active
    )

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[User]:
        return get_users( )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_user(self, name:str, email:str, hashed_password: str, is_active: bool) -> User:
        return add_user(
            name=name, 
            email=email, 
            hashed_password=hashed_password, 
            is_active=is_active
        )

    # users: List[User] = strawberry.field(resolver=get_users)

# def get_users(keys: List[int], db: Session = Depends(get_db)) -> List[User]:
#     return db.query(models.User).all()

# @strawberry.type
# class Query:
#     @strawberry.field
#     def users(self) -> List[User]:
#         db = SessionLocal()
#         users = db.query(models.User).all()
#         db.close()
#         return users

#     @strawberry.field
#     def items(self)-> List[Item]:
#         db = SessionLocal()
#         users = db.query(models.Item).all()
#         db.close()
#         return users
        


# strawberry_sqlalchemy_mapper.finalize()
schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)