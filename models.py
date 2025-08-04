from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Industry(Base):
    __tablename__ = "industries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    industry_name = Column(String(255), nullable=False)  # Specify length for MySQL
    category = Column(String(100), nullable=False)       # Specify length for MySQL
    parent_id = Column(Integer, ForeignKey("industries.id"))