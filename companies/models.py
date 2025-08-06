# companies/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base  # Import Base from database.py

class Company(Base):
    __tablename__ = "companies"  # Fixed: was 'tablename', should be '__tablename__'

    record_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_group_print_name = Column(String(255), nullable=False)
    company_group_data_type = Column(Enum('Company', 'Group', 'Division'), nullable=False)
    parent_id = Column(Integer, ForeignKey('companies.record_id', ondelete='CASCADE'), nullable=True)
    legal_name = Column(String(255), nullable=True)  # Changed from nullable=False to nullable=True
    other_names = Column(Text, nullable=True)
    imports = Column(Enum('Y', 'N'), default='N')
    exports = Column(Enum('Y', 'N'), default='N')
    manufacture = Column(Enum('Y', 'N'), default='N')
    distribution = Column(Enum('Y', 'N'), default='N')
    wholesale = Column(Enum('Y', 'N'), default='N')
    retail = Column(Enum('Y', 'N'), default='N')
    services = Column(Enum('Y', 'N'), default='N')
    online = Column(Enum('Y', 'N'), default='N')
    soft_products = Column(Enum('Y', 'N'), default='N')

    # Self-referencing relationship
    parent = relationship("Company", remote_side=[record_id], backref="children")