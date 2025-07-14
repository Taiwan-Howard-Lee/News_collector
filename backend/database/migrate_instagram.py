#!/usr/bin/env python3
"""
Database migration script to add Instagram-style fields to the resources table.
Run this script to update your existing database with the new fields.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.database.connection import engine, DATABASE_URL
from backend.models.resource import Base, Resource

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Run the Instagram-style fields migration"""
    try:
        # Use the existing database connection
        database_url = DATABASE_URL
        logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        
        # Check if we're using PostgreSQL or SQLite
        is_postgresql = database_url.startswith('postgresql')
        
        with engine.connect() as conn:
            # Check if the new columns already exist
            if is_postgresql:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'resources' AND column_name IN (
                        'image_url', 'hashtags', 'likes_count', 'comments_count', 
                        'shares_count', 'engagement_score'
                    )
                """))
            else:
                # For SQLite, we'll try to add the columns and catch the error if they exist
                result = None
            
            existing_columns = [row[0] for row in result] if result else []
            
            # Add new columns if they don't exist
            columns_to_add = [
                ('image_url', 'VARCHAR(500)'),
                ('hashtags', 'TEXT' if not is_postgresql else 'JSONB'),
                ('likes_count', 'INTEGER DEFAULT 0'),
                ('comments_count', 'INTEGER DEFAULT 0'),
                ('shares_count', 'INTEGER DEFAULT 0'),
                ('engagement_score', 'FLOAT DEFAULT 0.0')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        alter_sql = f"ALTER TABLE resources ADD COLUMN {column_name} {column_type}"
                        logger.info(f"Adding column: {column_name}")
                        conn.execute(text(alter_sql))
                        conn.commit()
                        logger.info(f"Successfully added column: {column_name}")
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                            logger.info(f"Column {column_name} already exists, skipping")
                        else:
                            logger.error(f"Error adding column {column_name}: {e}")
                            raise
                else:
                    logger.info(f"Column {column_name} already exists, skipping")
            
            # Update existing records with default values
            logger.info("Updating existing records with default values...")
            
            update_queries = [
                "UPDATE resources SET likes_count = 0 WHERE likes_count IS NULL",
                "UPDATE resources SET comments_count = 0 WHERE comments_count IS NULL", 
                "UPDATE resources SET shares_count = 0 WHERE shares_count IS NULL",
                "UPDATE resources SET engagement_score = 0.0 WHERE engagement_score IS NULL"
            ]
            
            for query in update_queries:
                try:
                    conn.execute(text(query))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error updating defaults: {e}")
            
            # Generate hashtags for existing records
            logger.info("Generating hashtags for existing records...")
            
            if is_postgresql:
                # For PostgreSQL, we can use JSONB
                conn.execute(text("""
                    UPDATE resources 
                    SET hashtags = '["Singapore"]'::jsonb 
                    WHERE hashtags IS NULL
                """))
            else:
                # For SQLite, store as JSON string
                conn.execute(text("""
                    UPDATE resources 
                    SET hashtags = '["Singapore"]' 
                    WHERE hashtags IS NULL
                """))
            
            conn.commit()
            
            # Generate engagement scores based on relevance
            logger.info("Calculating initial engagement scores...")
            conn.execute(text("""
                UPDATE resources 
                SET engagement_score = relevance_score * 10
                WHERE engagement_score = 0.0 AND relevance_score > 0
            """))
            conn.commit()
            
        logger.info("Migration completed successfully!")
        
        # Verify the migration
        logger.info("Verifying migration...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM resources WHERE hashtags IS NOT NULL"))
            count = result.scalar()
            logger.info(f"Records with hashtags: {count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM resources WHERE engagement_score > 0"))
            count = result.scalar()
            logger.info(f"Records with engagement scores: {count}")
        
        logger.info("Migration verification completed!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def rollback_migration():
    """Rollback the Instagram-style fields migration"""
    try:
        database_url = DATABASE_URL
        
        is_postgresql = database_url.startswith('postgresql')
        
        with engine.connect() as conn:
            columns_to_remove = [
                'image_url', 'hashtags', 'likes_count', 
                'comments_count', 'shares_count', 'engagement_score'
            ]
            
            for column_name in columns_to_remove:
                try:
                    if is_postgresql:
                        alter_sql = f"ALTER TABLE resources DROP COLUMN IF EXISTS {column_name}"
                    else:
                        # SQLite doesn't support DROP COLUMN easily, so we'll skip rollback for SQLite
                        logger.warning(f"SQLite doesn't support DROP COLUMN. Skipping rollback for {column_name}")
                        continue
                    
                    logger.info(f"Removing column: {column_name}")
                    conn.execute(text(alter_sql))
                    conn.commit()
                    logger.info(f"Successfully removed column: {column_name}")
                except Exception as e:
                    logger.error(f"Error removing column {column_name}: {e}")
        
        logger.info("Rollback completed!")
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Instagram-style fields migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    args = parser.parse_args()
    
    if args.rollback:
        logger.info("Starting migration rollback...")
        rollback_migration()
    else:
        logger.info("Starting migration...")
        run_migration()
