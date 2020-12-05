# Third party imports
from flask_migrate import Migrate, MigrateCommand

# Local application imports
from app import create_app
from app.extensions import db
from manager import Manager
from manager.database import manager as database_manager

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command("db", database_manager)
manager.add_command("alembic", MigrateCommand)


@manager.command
def run():
    """ Run locally, host and port set by configuration. """
    app.run()


@manager.shell
def make_shell_context():
    """ Configure shell setup. """
    # http://flask-script.readthedocs.org/en/latest/#default-commands
    return dict(app=app, db=db)


if __name__ == "__main__":
    manager.run()
