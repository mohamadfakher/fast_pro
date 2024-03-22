#models/models.py
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=225, null=False, unique=True)
    password = fields.CharField(max_length=225, null=False)

user_pydantic = pydantic_model_creator(User, name="User")







'''
from tortoise import Model, fields
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=225, null=False, unique=True)
    password = fields.CharField(max_length=225, null=False)

class Role(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=80, unique=True)
    description = fields.CharField(max_length=255)

class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=225, null=False, index=True)
    description = fields.CharField(max_length=225, null=False, index=True)
    price = fields.DecimalField(max_digits=12, decimal_places=2)
    image_path = fields.CharField(max_length=225, null=False, default="productdefault.jpg")


user_pydantic = pydantic_model_creator(User, name="User")
role_pydantic = pydantic_model_creator(Role, name="Role")
product_pydantic = pydantic_model_creator(Product, name="Product")

'''
