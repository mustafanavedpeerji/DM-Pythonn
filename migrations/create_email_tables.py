# Email Tables Migration Script
# Creates email_directory and email_associations tables

from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    """Create email tables"""
    
    # Create email_directory table
    op.create_table(
        'email_directory',
        sa.Column('email_id', sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column('email_address', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('email_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.String(10), default="Active"),
    )
    
    # Create email_associations table
    op.create_table(
        'email_associations',
        sa.Column('association_id', sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column('email_id', sa.Integer, sa.ForeignKey('email_directory.email_id'), nullable=False, index=True),
        sa.Column('company_id', sa.Integer, nullable=True, index=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('person_id', sa.Integer, nullable=True, index=True),
        sa.Column('association_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
    )

def downgrade():
    """Drop email tables"""
    op.drop_table('email_associations')
    op.drop_table('email_directory')

# Manual execution script for systems without Alembic
def create_tables_manual():
    """Manual table creation for direct execution"""
    import sqlite3
    
    # Connect to database
    conn = sqlite3.connect('business_management.db')
    cursor = conn.cursor()
    
    try:
        # Create email_directory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_directory (
                email_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address VARCHAR(255) NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                email_type VARCHAR(50),
                description TEXT,
                is_active VARCHAR(10) DEFAULT 'Active'
            )
        ''')
        
        # Create index on email_address
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_address ON email_directory(email_address)')
        
        # Create email_associations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_associations (
                association_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                company_id INTEGER,
                department VARCHAR(100),
                person_id INTEGER,
                association_type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                notes TEXT,
                FOREIGN KEY (email_id) REFERENCES email_directory (email_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_associations_email_id ON email_associations(email_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_associations_company_id ON email_associations(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_associations_person_id ON email_associations(person_id)')
        
        conn.commit()
        print("Email tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables_manual()