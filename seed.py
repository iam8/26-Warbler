# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
Seed database with sample data from CSV Files.
"""

from csv import DictReader

from app import app, db
from models import User, Message, Follow


if __name__ == "__main__":

    with app.app_context():
        db.drop_all()
        db.create_all()

        with open('generator/users.csv') as users:
            db.session.bulk_insert_mappings(User, DictReader(users))

        with open('generator/messages.csv') as messages:
            db.session.bulk_insert_mappings(Message, DictReader(messages))

        with open('generator/follows.csv') as follows:
            db.session.bulk_insert_mappings(Follow, DictReader(follows))

        db.session.commit()
