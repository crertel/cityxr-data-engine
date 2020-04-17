from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

# keep this here, don't move it, don't delete it...
# it's a structural unused import
from app import views
