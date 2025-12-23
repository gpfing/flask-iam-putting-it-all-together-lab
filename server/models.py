from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String(128), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(255), nullable=True)
    
    @property
    def id(self):
        return self.user_id

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not readable")
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    recipe_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship('User', backref=db.backref('recipes', lazy=True))
    
    @property
    def id(self):
        return self.recipe_id
    
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions

    

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    image_url = fields.Str()
    bio = fields.Str()
    recipes = fields.List(fields.Nested(lambda: RecipeSchema(exclude=('user',))))

class RecipeSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    instructions = fields.Str(required=True)
    minutes_to_complete = fields.Int(required=True)
    user_id = fields.Int()
    user = fields.Nested(lambda: UserSchema(exclude=('recipes',)))