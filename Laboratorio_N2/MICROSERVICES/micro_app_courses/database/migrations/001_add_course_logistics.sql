-- Idempotent compatibility migration for the classroom/schedule contract.
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
