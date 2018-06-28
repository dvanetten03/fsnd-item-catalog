from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind=engine
# Base.metadata.bind(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Create temp user
user1 = User(name="Diane Van Etten", email="Diane.vanetten@gmail.com", picture="https://www.pexels.com/photo/yellow-flowers-on-brown-sand-1167465/")
session.add(user1)
session.commit()

#Create temp categories
category1 = Category(name="routers", user_id=1)
session.add(category1)
session.commit()

#Create items for temp category 1
item1 = Item(name="ubiquiti", description="main router", category=category1)
session.add(item1)
session.commit()

item2 = Item(name="ubiquiti", description="alternate router", category=category1)
session.add(item2)
session.commit()

item3 = Item(name="ubiquiti", description="object router", category=category1)
session.add(item3)
session.commit()

category2 = Category(name="switches")
session.add(category2)
session.commit()

#Create items for temp category 2
item1 = Item(name="ubiquiti", description="main switch", category=category2)
session.add(item1)
session.commit()

item2 = Item(name="ubiquiti", description="alternate switch", category=category2)
session.add(item2)
session.commit()

item3 = Item(name="ubiquiti", description="object switch", category=category2)
session.add(item3)
session.commit()

category3 = Category(name="access points")
session.add(category2)
session.commit()

#Create items for temp category 3
item1 = Item(name="ubiquiti", description="main access points", category=category3)
session.add(item1)
session.commit()

item2 = Item(name="ubiquiti", description="alternate access points", category=category3)
session.add(item2)
session.commit()

item3 = Item(name="ubiquiti", description="object access points", category=category3)
session.add(item3)
session.commit()

categories = session.query(Category).all()
for category in categories:
	print "The category is: " + category.name