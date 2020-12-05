# Third party imports
from faker import Faker
from flask_script import Manager, prompt_bool

# Local application imports
from app.extensions import db

manager = Manager(usage="Perform database operations")


@manager.command
def drop():
    """Drops database tables"""
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def seed():
    fake = Faker()

    # Local application imports
    from app.api.recipe import Recipe

    for _ in range(5):
        Recipe.seed(fake)


@manager.command
def create(seed=False):
    """Creates database tables from sqlalchemy models"""
    db.create_all()

    if seed is True:
        seed()


@manager.command
def recreate(seed=False):
    """Recreates database tables (same as issuing 'drop' and then 'create')"""
    drop()
    create(seed)
