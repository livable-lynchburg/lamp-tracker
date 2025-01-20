#import app object from FlaskApp package
from lamp-tracker_package import app

#run the app with built-in wsgi server if
#__init__.py is run directly and not imported
if __name__ == '__main__':
    app.run(debug=True)
