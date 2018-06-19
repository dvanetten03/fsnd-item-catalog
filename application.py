from flask import Flask, render_template
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# engine = create_engine('sqlite://itemcatalog.db')
# Base.metadata.bind = engine

# Add additional configuration to an existing sessionmaker() according to sqlalchemy
# DBSession = sessionmaker(bind=engine)
# session = DBSession

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


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)