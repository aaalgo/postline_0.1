#!/usr/bin/env python3
from sql_storage import create_engine, Base
import config

engine = create_engine(config.DB_URL)
Base.metadata.create_all(engine)