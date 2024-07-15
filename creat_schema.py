from sqlalchemy import create_engine
from model import Base
import config

engine = create_engine(config.db_sync_url)
Base.metadata.create_all(bind=engine)