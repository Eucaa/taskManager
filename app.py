import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # This routing_id is needed to obtain the parameter of ('/edit_task/<task_id>').

# MongoDB stores its data in a JSON like format called BSON, which you might need to use sometimes.

app = Flask(__name__)

# Is optional, but inclusion is good.
app.config["MONGO_DBNAME"] = 'task_manager'
app.config["MONGO_URI"] = os.environ.get('MONGODB_CONNECTIONSTRING', 'mongodb://localhost') +  "/" + app.config["MONGO_DBNAME"] + "?retryWrites=true&w=majority"

mongo = PyMongo(app)

# Connect to the database through decorators.
@app.route('/')
@app.route('/get_tasks')  # The name of the (Routing Identifier) string must can be connected to the function, which will be called by default one's it's in place.
def get_tasks():
    return render_template("tasks.html", tasks=mongo.db.tasks.find())
# This will request to make a connection to a template called tasks.html (located in the templates-folder).
# tasks=mongo.db.task.find()) will make a "call" to the requested collection and return the data from it.


# Create a Routing-id that will re-direct to the addtask.html page)
@app.route('/add_task')
def add_task():
    print("Updated")
    return render_template('addtask.html', categories=mongo.db.categories.find())


@app.route('/insert_task', methods=['POST']) #The method for insert_task is 'POST', as you are submitting (en therefor posting) something.
def insert_task():
    tasks = mongo.db.tasks  # Get the tasks collection from Mongo.
    tasks.insert_one(request.form.to_dict()) #Whenever you submit information to a URI or to a web location, it is submitted in the form of a request object.
    # Get that request.form and turn it into a dictionary for Mongo to read. Active fields or with data will be submitted and will create a new doc in the tasks collection.
    return redirect(url_for('get_tasks'))
    # Redirect to get_tasks, so we can view that new task in our collection.


#If you want to edit a task, it actually means you want to edit the properties associated with it (e.g. the name, date, description etc.).
@app.route('/edit_task/<task_id>') #A guaranteed way of targeting the task we're looking for is to use its ID, which is similar to its primary key in a relational database.
def edit_task(task_id):
    the_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    # Look for a particular task in the MongoDB task collection (find_one), look for a match of the _id as a parameter and warp in an object, 
    # and make it a format (task_id) that can be read by Mongo.
    all_categories = mongo.db.categories.find()  # Retrieve a list of all collections so you can fill a form of the returned task (which returned from the categories) with it.
    return render_template('edittask.html', task=the_task, categories=all_categories) #Pass the task and the categories back to the edittask.html file.


@app.route('/update_task/<task_id>', methods=['POST'])  # Get the route to the update_task function with parameter <task_id> to post the changes into the database.
def update_task(task_id):  # Create the update_task function and find the data through the parameter task_id.
    tasks = mongo.db.tasks  # Var tasks stands for the tasks field table in the MongoDB collection of task_manager.
    tasks.update({'_id': ObjectId(task_id)},  # Get the _id of the requested task and update the following areas, if needed.
    {
        'task_name':request.form.get('task_name'),
        'category_name':request.form.get('category_name'),
        'task_description': request.form.get('task_description'),
        'due_date': request.form.get('due_date'),
        'is_urgent':request.form.get('is_urgent')
    })
    return redirect(url_for('get_tasks'))

@app.route('/get_categories')  # Get the route to the get_categories function.
def get_categories():  # Create the get_categories function to find the categories table.
    return render_template('categories.html', categories=mongo.db.categories.find())  # Find the categories field in mongoDB and give the info to the categories.html file for process.  


@app.route('/edit_category/<category_id>')  # Get the route to the edit_category function an it's value.
def edit_category(category_id):  # Create the edit_categories function, with the category_id parameter.
    return render_template('editcategory.html',
    category=mongo.db.categories.find_one({'_id': ObjectId(category_id)}))  # Find the requested category ID through MongoDB and fill it in at the editcategory.html file.


@app.route('/update_category/<category_id>', methods=['POST'])  # Get the route to the update_category function with parameter <category_id> to post the changes into the database.
def update_category(category_id):  # Create the update_category function and find the data through the parameter category_id.
    mongo.db.categories.update(  # Call the categories collection from MongoDB en then update:.
        {'_id': ObjectId(category_id)},  # Indentify the _id and the field with the category_id...
        {'category_name': request.form.get('category_name')})  # ... Indentify the key (category_name), and follow up with the form to request and POST the update.
    return redirect(url_for('get_categories'))  # Return the get_categories function to view the update of the collection.


@app.route('/delete_category/<category_id>')
def delete_category(category_id):  # Pass in the category_id as a parameter which is to be used to locate and remove the appointed category document from the categories collection.  
    mongo.db.categories.remove({'_id': ObjectId(category_id)})
    return redirect(url_for('get_categories'))  # This will make a call to the categories collection and return what categories are left in the database.


@app.route('/insert_category', methods=['POST'])  # Use the insert_category route to post the update as given in the function below.
def insert_category():
    category_doc = {'category_name': request.form.get('category_name')}  # Create another variable and add some BSON to it, to request a form. Get it based on teh category_name.
    mongo.db.categories.insert_one(category_doc)  # Add category_doc (with the new inserted category) into the categories table in the task_manager collection on MongoDB.
    return redirect(url_for('get_categories'))  # Redirect the result back into the get_categories function, onto the categories.html template.


# You do need a function that will allow you to add a new category in the first place tho, by rendering it through a html view: 
@app.route('/add_category')
def add_category():
    return render_template('addcategory.html')  # The rendering of a template is the same as the redering of a view. Thus, a template is also called a view.

if __name__ == '__main__':
    print(os.environ.get('IP'))
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '8080')),
            debug=True)
