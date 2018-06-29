import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Table for User Information
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

# Table for Category Information
class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250))
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		# Returns object data in easily serializable forma
		return {
		'name'			:self.name,
		'id'			:self.id,
		'user_id'		:self.user.id,
		'description'	:self.description
		}

# Table for Item Information
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
		# Returns object data in easily serializable forma
		return {
		'category'		:self.category.name,
		'description'	:self.description,
		'id'			:self.id
		}

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
	