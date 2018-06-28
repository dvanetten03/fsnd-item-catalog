# Use file to populate database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine
# Base.metadata.bind(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Create user
user1 = User(name="Diane Van Etten", email="Diane.vanetten@gmail.com", picture="https://www.pexels.com/photo/yellow-flowers-on-brown-sand-1167465/")
session.add(user1)
session.commit()

#Create categories
category1 = Category(name="Router")
session.add(category1)
session.commit()

#Create items for temp category 1
item1 = Item(name="UniFi Security Gateway", user_id=1, description="The UniFi security gateway extends the UniFi Enterprise System to provide cost-effective, reliable routing and advanced security for your network.", category=category1)
session.add(item1)
session.commit()

item2 = Item(name="UniFi Security Gateway Pro $", user_id=1, description="Enterprise Gateway Router with Gigabit Ethernet", category=category1)
session.add(item2)
session.commit()

item3 = Item(name="UniFi Security Gateway XG8", user_id=1, description="Gateway Router with 8 10G SFP+ and One 1G RJ45", category=category1)
session.add(item3)
session.commit()

category2 = Category(name="Switch")
session.add(category2)
session.commit()

#Create items for category 2
item1 = Item(name="UniFi Switch PoE 24/48", user_id=1, description="Managed PoE+ gigabit switch with SFP", category=category2)
session.add(item1)
session.commit()

item2 = Item(name="UniFi Switch 8", user_id=1, description="Fully managed gigabit switch", category=category2)
session.add(item2)
session.commit()

item3 = Item(name="UniFi Switch 24/48", user_id=1, description="Managed gigabit switch with SFP", category=category2)
session.add(item3)
session.commit()

category3 = Category(name="Access point")
session.add(category3)
session.commit()

#Create items for category 3
item1 = Item(name="UniFi AP", user_id=1, description="Indoor 802.11n access point", category=category3)
session.add(item1)
session.commit()

item2 = Item(name="UniFi AP Outdoor", user_id=1, description="UniFi AP Outdoor 802.11n access point", category=category3)
session.add(item2)
session.commit()

item3 = Item(name="PrismStation AC", user_id=1, description="Shielded airMAX ac Basestation with airPrism Technology", category=category3)
session.add(item3)
session.commit()

category4 = Category(name="Antennae")
session.add(category4)
session.commit()

#Create items for category 4
item1 = Item(name="airFiber X Antenna", user_id=1, description="Slant 45 Antenna for airFiber", category=category4)
session.add(item1)
session.commit()

item2 = Item(name="airFiber NxN", user_id=1, description="Scalable airFiber MIMO Multiplexer", category=category4)
session.add(item2)
session.commit()

item3 = Item(name="IsoBean", user_id=1, description="Isolator Radome for 620mm Dish Reflector", category=category4)
session.add(item3)
session.commit()

category5 = Category(name="CPE")
session.add(category5)
session.commit()

#Create items for category 5
item1 = Item(name="UFiber Nano G", user_id=1, description="GPON Optical Network Unit, a robust, high-performance GPON CPE that features an informational LED display and a sleek, sophisticated industrial design.", category=category5)
session.add(item1)
session.commit()

item2 = Item(name="UFiber loco", user_id=1, description="Low-cost GPON Optical Network Unit sporting a sleek industrial design that features extremely low power consumption and two power options.", category=category5)
session.add(item2)
session.commit()

item3 = Item(name="UFiber OLT", user_id=1, description="GPON Optical Line Terminal that can be deployed by anyone.", category=category5)
session.add(item3)
session.commit()

categories = session.query(Category).all()
for category in categories:
	print "The category is: " + category.name