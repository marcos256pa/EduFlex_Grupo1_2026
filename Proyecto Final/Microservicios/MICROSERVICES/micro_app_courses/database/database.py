import os
from sqlalchemy import MetaData, Table, create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://courses_db_data:2wvTyzhft81R8f6@micro_db_courses:5432/micro_db_courses")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Upgrade old Spanish column names without losing existing course logistics.
with engine.begin() as connection:
    connection.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'courses' AND column_name = 'aula')
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'courses' AND column_name = 'classroom') THEN
                ALTER TABLE courses RENAME COLUMN aula TO classroom;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'courses' AND column_name = 'horario')
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'courses' AND column_name = 'schedule') THEN
                ALTER TABLE courses RENAME COLUMN horario TO schedule;
            END IF;
        END $$;
        ALTER TABLE courses
            ADD COLUMN IF NOT EXISTS classroom VARCHAR(120) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS schedule VARCHAR(160) NOT NULL DEFAULT '';
    """))

courses = Table("courses", metadata, autoload_with=engine)
