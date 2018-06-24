from flask import Flask, render_template, url_for, request
from flask import jsonify, flash, redirect, make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import httplib2
import random
import string
import json
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to database
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)

#Add additional configuration to an existing sessionmaker() according to sqlalchemy
DBSession = sessionmaker(bind=engine)
session = DBSession

# Creating anti-forgery state token
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	# Render the login session
	return render_template('login.html', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	#Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data
	try:
		#Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Check that the access token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	#If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Verify that the access token is used for the intended user
	g_id = credentials.id_token['sub']
	if result['user_id'] != g_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given userID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID doesn't match app's."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Check to see if user is already logged in
	stored_access_token = login_session.get('access_token')
	stored_g_id = login_session.get('g_id')
	if stored_access_token is not None and g_id == stored_g_id:
		response = make_response(json.dumps('Current user is already logged in.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Store the access token in the session for later use.
	login_session['provider'] = 'google'
	login_session['access_token'] = credentials.access_token
	login_session['g_id'] = g_id

	#Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = anwer.json()

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["email"]

	#See if a user exists, if it doesn't then make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id
	login_session['provider'] = 'google'

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']

	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' "style = "width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
	flash("you are now logged in as %s" %login_session['username'])
	print ("done!")
	return output

#DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
	#Only disconnect a connected user
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
		#Execute HTTP GET request to revoke current token.
		access_token = credentials.access_token
		url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %access_token
		h = httplib2.Http()
		result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		#Reset the user's session.
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

#Add facebook login api
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = request.data
	print ("access token received %s") %access_token

	# Exchange client token for long-lived server-side token with Get /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&fb_exchange_token={short-lived-token}
	app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
	app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	# Use token to get user info from API
	userinfo_url = "https://graph.facebook.com/v2.8/me"
	#strip expire tag from access token
	token = result.split(',')[0].split(':')[1].replace('"', '')

	url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name, id, email' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	data = json.loads(result)

	login_session['provider'] = 'facebook'
	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['facebook_id'] = data['id']

	login_session['access_token'] = token

	#Get user picture
	url = "https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200" % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data["data"]["url"]

	# See if a user exists, if it doesn't, make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id - createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1> Welcome, '
	output =+ login_session['username']

	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px; border-radius :150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
	flash("you are now logged in as %s" %login_session['username'])
	return output

#Disconnect from fblogin
@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	access_token = login_session['access_token']
	url = 'https://graph.facebook.com/%s/permissions' % (facebook_id, access_token)
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	return "You have been logged out"

@app.route('/disconnect')
def disconnect():
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['g_id']
			del login_session['credentials']
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']

		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		flash ("You have successfully been logged out.")
		return redirect(url_for('showCatalog'))
	else:
		flash("You were not logged in to begin with!")
		redirect(url_for('showCatalog'))

#JSON APIs to view Catalog Information
@app.route('/catalog/<int: category_id>/category/JSON')
def catalogCategoryJSON(category_id):
	catalog = session.query(Catalog).filter_by(id = category_id).one()
	items = session.query(categoryItem).filter_by(category_id = category_id).all()
	return jsonify(CategoryItems=[i.serialize for i in items])

@app.route('/catalog/<int: category_id>/category/<int: item_id>/JSON')
def categoryItemJSON(category_id, item_id):
	CategoryItem = session.query(CategoryItem).filter_by(id = item_).one()
	return jsonify(CategoryItem = CategoryItem.serialize)

@app.route('/catalog/JSON')
def categoryJSON():
	catalog = session.query(Catalog).all()
	return jsonify(catalog = [r.serialize for r in catalog])


# Show all catalog categories
@app.route('/')
@app.route('/catalog')
def showCatalog():
	#return "This page will show all catalog categories"
	return render_template('showcatalog.html')

# Add new catalog category
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategory():
	#return "This page will be for making a new category"
	return render_template('newcategory.html')

# Edit catalog category
@app.route('/catalog/<int:category_id>/edit', methods = ['GET', 'POST'])
def editCategory():
	#return "This page will be for editing catalog category %s" %category_id
	return render_template('editcategory.html')

# Delete catalog category
@app.route('/catalog/<int:category_id>/delete', methods = ['GET', 'POST'])
def deleteCategory():
	#return "This page will be for deleting category %s" %category_id
	return render_template('deletecategory.html')

# Show a category's items
@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showItems():
	#return "This page is the item list for category %s" %category_id
	return render_template('showitems.html')

# Make a new item for a category
@app.route('/catalog/<int:category_id>/item/new', methods = ['GET', 'POST'])
def newCategoryItem():
	#return "This page is for making a new item for a category %s" %category_id
	return render_template('newcategoryitem.html')

# Edit a category item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit')
def editCategoryItem():
	#return "This page is for editing category item %s" %item_id
	return render_template('editcategoryitem.html')

# Delete a category item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete')
def deleteCategoryItem():
	#return "This page is for deleting category item %s" %item_id
	return render_template('deletecategoryitem.html')

# User Helper functions
def createUser(login_session):
	newUser = User(username=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	return user.id

def getUserInfo(user_id):
	user=session.query(User).filter_by(id=user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except NoResultFound:
		return None


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)