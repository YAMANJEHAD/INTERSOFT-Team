# database.py

from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 1. الاتصال بالقاعدة - ملف SQLite
engine = create_engine('sqlite:///tasks.db')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 2. نموذج المهمة (كل صف في الجدول)
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    employee = Column(String)
    date = Column(String)
    day = Column(String)
    shift = Column(String)
    department = Column(String)
    category = Column(String)
    status = Column(String)
    priority = Column(String)
    description = Column(String)
    submitted = Column(DateTime, default=datetime.datetime.utcnow)

# 3. إنشاء الجداول فعليًا
Base.metadata.create_all(bind=engine)
