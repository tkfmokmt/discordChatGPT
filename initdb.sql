create table IF NOT EXISTS reply_channel_ids (
channel_id varchar(100) PRIMARY KEY
);

create table IF NOT EXISTS chat_histories (
seq SERIAL NOT NULL,
channel_id varchar(100),
role varchar(100),
content text
);

create table IF NOT EXISTS ai_personalitys (
channel_id varchar(100) PRIMARY KEY,
personality_text text
);

