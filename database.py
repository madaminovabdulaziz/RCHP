# import logging
# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# # Load variables from .env file
# load_dotenv()

# logging.basicConfig(level=logging.INFO)

# # Read from environment variables
# DB_CONFIG = {
#     'username': os.getenv('DB_USERNAME'),
#     'password': os.getenv('DB_PASSWORD'),
#     'host': os.getenv('DB_HOST'),
#     'port': int(os.getenv('DB_PORT', 3306)),
#     'database': os.getenv('DB_NAME'),
#     'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
#     'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10))
# }

# # Build connection string
# DB_CONNECTION_STRING = (
#     f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@"
#     f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
# )

# # Create engine
# engine = create_engine(
#     DB_CONNECTION_STRING,
#     pool_size=DB_CONFIG['pool_size'],
#     max_overflow=DB_CONFIG['max_overflow']
# )

# # Session maker
# Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# # Base model
# Base = declarative_base()

# def get_db():
#     """Generator function to yield a database session."""
#     db = Session()
#     try:
#         logging.info("New database session created.")

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MYSQL_HOST = "mysql.railway.internal"
MYSQL_DATABASE = "railway"
MYSQL_USER = "root"
MYSQL_PASSWORD = "lBTazBqQODWYODlbhyEkZwmEHaDRCEQI"
MYSQL_PORT = 3306

connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine = create_engine(connection_string, pool_size=100, max_overflow=100)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
	db = Session()
	try:
		yield db
	finally:
		db.close()
#         yield db
#     finally:
#         db.close()
#         logging.info("Database session closed.")
