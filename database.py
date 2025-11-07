from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from db_models import DB

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
DB.metadata.create_all(engine)