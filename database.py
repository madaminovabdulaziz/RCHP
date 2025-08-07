import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)

DB_CONFIG = {
    'username': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': 3306,
    'database': 'rchp_hotel',
    'pool_size': 20,
    'max_overflow': 10
}


DB_CONNECTION_STRING = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@" \
                        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


engine = create_engine(DB_CONNECTION_STRING, pool_size=DB_CONFIG['pool_size'], max_overflow=DB_CONFIG['max_overflow'])

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base = declarative_base()


def get_db():
    """Generator function to yield a database session."""
    db = Session()
    try:
        logging.info("New database session created.")
        yield db
    finally:
        db.close()
        logging.info("Database session closed.")
