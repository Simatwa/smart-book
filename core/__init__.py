from .app import application
from .accounts.views import app as account_view
from .notes.views import app as notes_view
from flask_migrate import Migrate
from .models import db

# Register Blueprints
application.register_blueprint(account_view, url_prefix="/accounts", cli_group="user")
application.register_blueprint(notes_view, url_prefix="/notes", cli_group="notes")

migrate = Migrate()
migrate.init_app(application, db)

# Init db schema

with application.app_context():
    db.create_all()
