print(0)
import jwt
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

from .context import Base, get_session

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


print(1)

class ContextManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ContextManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    

    def __init__(self, context_object):
        if not hasattr(self, 'is_initialized'):
            self.context = context_object
            self.Model = Base
            self.Column = Column
            self.String = String
            self.Integer = Integer
            self.Float = Float
            self.Text = Text
            self.Boolean = Boolean
            self.DateTime = DateTime
            self.ForeignKey = ForeignKey
            self.relationship = relationship
            self.context = None  # Start with no context
            self.is_initialized = True

    def set_context(self, context_object):
        if not isinstance(context_object, ContextObject):
            raise ValueError("context_object must be an instance of ContextObject or its subclass")
        self.context = context_object

    def operate(self):
        if self.context is None:
            raise ValueError("Context has not been set.")
        return self.context.get()




class ContextObject:
    def __init__(self):
        session = get_session()
        self.session = session
    
    def get(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def close_session(self):
        self.session.close()

class Assistants(ContextObject):
    def __init__(self, token, user_type):
        print(1)
        super().__init__()
        print(2)
        if user_type == "customer":
            print(3)
            
            self.close_session()
            print(4)
            user = None
            if user:
                return {
                    'status_code': 200,
                    'body': f'Customer Found! Your name is {user.username}'
                }
            else:
                return {
                    'status_code': 400,
                    'body': f'Customer was not found, token was {token}'
                }
        else:
            return {
                'status_code': 400,
                'body': f'User was not found, token was {token}, user_type was {user_type}'
            }




class AdminContext(ContextObject):
    def get(self):
        # Customize this method for Admin user handling
        return f"Admin Access: Token ID {self.token_id} for user type {self.user_type}"

class GuestContext(ContextObject):
    def get(self):
        # Customize this method for Guest user handling
        return f"Guest Access: Token ID {self.token_id} for user type {self.user_type}"

class MemberContext(ContextObject):
    def get(self):
        # Customize this method for Member user handling
        return f"Member Access: Token ID {self.token_id} for user type {self.user_type}"
