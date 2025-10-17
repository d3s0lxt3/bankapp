import os
import logging
import random
import string
from contextlib import contextmanager
from datetime import datetime, timedelta
from faker import Faker

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError

from core.models import Base, User, Card

logger = logging.getLogger("app")

DB_ENGINE = None
DB_SESSION = None
fake = Faker("ru_RU")


def _get_database_url():
    db_path = "/var/www/html/bankapp/data/bankapp.sqlite3"
    return f"sqlite:///{db_path}"


def init_db(app=None):
    global DB_ENGINE, DB_SESSION

    db_url = _get_database_url()
    echo_flag = os.environ.get("SQLALCHEMY_ECHO", "false").lower() in ("1", "true", "yes")

    try:
        DB_ENGINE = create_engine(db_url, echo=echo_flag, future=True)
        logger.info("Engine created successfully.")
    except Exception as e:
        logger.exception("Failed to create engine for '%s': %s", db_url, e)
        raise

    try:
        Base.metadata.drop_all(DB_ENGINE)
        Base.metadata.create_all(DB_ENGINE)
        logger.info("Database schema recreated successfully.")
    except Exception:
        logger.exception("Failed to recreate tables.")

    session_factory = sessionmaker(bind=DB_ENGINE, autoflush=False, autocommit=False, future=True)
    DB_SESSION = scoped_session(session_factory)

    seed_database(DB_SESSION())

    if app is not None:
        try:
            @app.teardown_appcontext
            def remove_db_session(exc):
                if DB_SESSION is not None:
                    DB_SESSION.remove()
        except Exception:
            logger.exception("Failed to register teardown_appcontext for DB session removal")


def seed_database(session):
    logger.info("Seeding database with 500 random users...")
    try:
        session.query(Card).delete()
        session.query(User).delete()
        session.commit()

        users = []
        cards = []

        for i in range(500):
            username = fake.unique.user_name() + str(random.randint(10, 9999))
            fullname = fake.name()
            email = fake.unique.email()
            password_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
            is_admin = (i == 0)

            user = User(
                username=username,
                password_hash=password_hash,
                fullname=fullname,
                email=email,
                is_admin=is_admin
            )
            users.append(user)

        session.add_all(users)
        session.commit()
        logger.info("500 random users created successfully.")

        logger.info("Generating cards for each user...")

        for user in users:
            for _ in range(random.randint(1, 2)):
                card_number = ''.join(random.choices(string.digits, k=16))
                card_type = random.choice(["Visa", "MasterCard", "Mir"])
                balance = round(random.uniform(1000, 100000), 2)
                currency = "RUB"
                expiry_date = datetime.now() + timedelta(days=365 * random.randint(1, 5))
                cvv = ''.join(random.choices(string.digits, k=3))

                card = Card(
                    user_id=user.id,
                    card_number=card_number,
                    card_type=card_type,
                    balance=balance,
                    currency=currency,
                    expiry_date=expiry_date,
                    cvv=cvv
                )
                cards.append(card)

        session.add_all(cards)
        session.commit()
        logger.info("Cards generated successfully for all users.")

    except Exception as e:
        session.rollback()
        logger.exception("Error during database seeding: %s", e)
    finally:
        session.close()


@contextmanager
def get_db_session():
    global DB_SESSION
    if DB_SESSION is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    session = DB_SESSION()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection(timeout_seconds: int = 5) -> bool:
    global DB_ENGINE
    if DB_ENGINE is None:
        raise RuntimeError("Engine not initialized. Call init_db(app) first.")
    try:
        with DB_ENGINE.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError as oe:
        logger.warning("OperationalError while testing DB connection: %s", oe)
        return False
    except Exception as e:
        logger.exception("Unexpected error while testing DB connection: %s", e)
        return False
