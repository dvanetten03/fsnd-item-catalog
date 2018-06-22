import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return{
		'name'		:self.name,
		'id'		:self.id,
		'user_id'	:self.user.id
		}

class Item(Base):
	__tablename__ = 'item'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	description = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id'))
	user_id = Column(Integer, ForeignKey('user.id'))
	category = relationship(Category)
	user = relationship(User)

	@property
	def serialize(self):
		return{
		'category'		:self.category.name,
		'description'	:self.description,
		'id'			:self.id
		}

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
	