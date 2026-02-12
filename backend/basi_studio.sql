CREATE SCHEMA studio;

SELECT current_schema();

SHOW search_path;

SET search_path TO studio,public;

--I NEED JESUS

--pinakas pliroforias users
CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	email TEXT UNIQUE NOT NULL, 
	passwords TEXT NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	last_login TIMESTAMPTZ
);

--extra pinakas gia locations
CREATE TABLE user_locations(
	loc_id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(user_id) on delete cascade,
	long FLOAT,
	lat FLOAT,
	location_name TEXT,
	timestp TIMESTAMPTZ DEFAULT NOW()
);

--pinakas me dedomena emotibit raw
CREATE TABLE emotibit(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(user_id) on delete cascade,
	sensor_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	eda_value FLOAT,
	ppg_red FLOAT,
	ppg_infrared FLOAT,
	temperature FLOAT,
	acc_x FLOAT	
);

/*CREATE INDEX idx_emotibit_u_t 
on emotibit(user_id, sensor_timestamp);*/

--anaparastasi tou agxous
CREATE TABLE anxiety_level(
	times TIMESTAMPTZ NOT NULL,
	user_id INT REFERENCES users(user_id) on delete cascade,
	timestam TIMESTAMPTZ DEFAULT NOW(),
	anxiety_score INT CHECK (anxiety_score between 0 and 100),
	source_type VARCHAR(50) DEFAULT 'emotibit_eda',
	is_high BOOLEAN DEFAULT FALSE
);

-- Turn this into a hypertable if using TimescaleDB (Optional but recommended)
-- SELECT create_hypertable('stress_levels', 'time');

-- 2. Create an index on (user_id, time) for fast history lookups
CREATE INDEX idx_stress_user_time ON anxiety_level (user_id, times DESC);

-- 3. (Optional) Materialized View for "Daily Summary" 
-- If your app gets slow, you can use this to pre-calculate daily averages.
-- For now, standard queries using DATE_TRUNC are likely fine for an MVP.
CREATE MATERIALIZED VIEW daily_anx_summary AS
SELECT
    user_id,
    DATE_TRUNC('day', times) AS day,
    ROUND(AVG(anxiety_score), 1) AS avg_anx,
    MAX(anxiety_score) AS max_anx,
    MIN(anxiety_score) AS min_anx,
    COUNT(*) AS reading_count -- Useful to know if a day has enough data
FROM
    anxiety_level
GROUP BY
    user_id,
    DATE_TRUNC('day', times)
WITH DATA;

-- Create an index to make querying this view instant
CREATE INDEX idx_daily_summary_user_day ON daily_anx_summary (user_id, day DESC);

REFRESH MATERIALIZED VIEW CONCURRENTLY daily_anx_summary;

--gia katigories ton texnikon 
CREATE TYPE technique_category AS ENUM (
	'meditation', 'self-hugging', 'positive- affirmations',
	'hand-techniques', 'breathing', 'muscle -relaxation', 'tapping'
);

--pinakas gia tis texnikes
CREATE TABLE relaxation_t(
	relax_id SERIAL PRIMARY KEY,
	name_tec TEXT NOT NULL,
	category technique_category NOT NULL,
	description TEXT,
	duration_m INT,
	--instruction_url TEXT, link video/audio
	recommened_anx_lvl INT DEFAULT 0 
	--created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ->mpa
);

--pinakas me ta faves 
CREATE TABLE favourites(
	user_id INT REFERENCES users(user_id) on delete cascade,
	relax_id INT REFERENCES relaxation_t(relax_id) on delete cascade,
	created_at TIMESTAMPTZ DEFAULT NOW(),  
	primary key (user_id, relax_id)
);

--suggestion gia texntikes 
CREATE TYPE log_status as ENUM(
'Completed',
'Abandoned',
'suggestion_Ingnored'
);

CREATE TABLE t_info(
log_id BIGSERIAL PRIMARY KEY,
user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
technique_id INT REFERENCES relaxation_t(relax_id) ON DELETE CASCADE,
timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
status log_status NOT NULL,
session_rate SMALLINT CHECK (session_rate >=1 and session_rate <=5),
trigger_metric VARCHAR(50)
);

/*--imerologio
CREATE TABLE calendar(
day_id DATE PRIMARY KEY NOT NULL,
day INT,
month INT,
year INT,
day_of_week INT,
day_of_year INT,
Week_of_year INT,
CONSTRAINT con_month CHECK (month >=1 AND month <=12),
CONSTRAINT con_day_of_year CHECK (day_of_year >=1 AND day_of_year <=366),
CONSTRAINT con_week_of_year CHECK (week_of_year >=1 AND week_of_year <=53)
);*/

-- dimiourgia ton event_type analoga me to ti event einai auto pou dimiourgei 
CREATE type event_type as ENUM(
	'Παρουσίαση',
	'Εξεταστική',
	'Παράδοση εργασίας',
	'Πρόοδος',
	'Άλλο'
);

--dimiourgia events
CREATE TABLE events(
	event_id TEXT PRIMARY KEY,
	user_id INT REFERENCES users(user_id) on delete cascade,
	title VARCHAR(150) NOT NULL,
	description TEXT,
	event_type event_type, 
	loc TEXT, 
	start_date DATE,
	end_date DATE,
	can_be_anx BOOLEAN DEFAULT true
	--eidopoiisi xreiazetai na einai edo -> FIREBASE 
);

--istoriko gia notifications
CREATE TABLE notification_history (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) on delete cascade,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trigger_reason VARCHAR(100), -- e.g., "High Stress Detected", "Upcoming Exam"
    suggested_technique_id INTEGER REFERENCES relaxation_t(relax_id),
    was_acknowledged BOOLEAN DEFAULT FALSE -- Did the user open/act on it?
);
