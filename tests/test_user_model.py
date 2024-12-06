import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_model.py import Users
from db.py import db

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

db.metadata.create_all(engine)

@pytest.fixture(scope='module')
def setup_database():
    db.metadata.create_all(engine)
    yield
    db.metadata.drop_all(engine)

def test_create_user(setup_database):
    user = Users(username="testuser", password="testpassword")
    session.add(user)
    session.commit()
    assert user.username == "testuser"
    assert len(user.salt) == 32
    assert len(user.password) == 64

def test_check_password(setup_database):
    user = Users(username="testuser2", password="testpassword")
    session.add(user)
    session.commit()
    assert user.check_password("testpassword") == True
    assert user.check_password("wrongpassword") == False

def test_duplicate_username(setup_database):
    user1 = Users(username="testuser3", password="testpassword")
    session.add(user1)
    session.commit()
    user2 = Users(username="testuser3", password="testpassword")
    with pytest.raises(IntegrityError):
        session.add(user2)
        session.commit()

def test_delete_user(setup_database):
    user = Users(username="testuser4", password="testpassword")
    session.add(user)
    session.commit()
    session.delete(user)
    session.commit()
    assert session.query(Users).filter_by(username="testuser4").first() is None

def test_update_password(setup_database):
    user = Users(username="testuser5", password="testpassword")
    session.add(user)
    session.commit()
    user.password = "newpassword"
    session.commit()
    assert user.check_password("newpassword") == True
    assert user.check_password("testpassword") == False