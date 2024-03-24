#models/models.py
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=225, null=False, unique=True)
    password = fields.CharField(max_length=225, null=False)

user_pydantic = pydantic_model_creator(User, name="User")

