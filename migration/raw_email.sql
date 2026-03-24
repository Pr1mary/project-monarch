CREATE TABLE raw_email (
	id int NOT NULL AUTO_INCREMENT,
	email_id varchar(255) NOT NULL,
	thread_id varchar(255),
	from_email varchar(255),
	to_email varchar(255),
	subject varchar(255),
	body text,
	created_at timestamp default current_timestamp(),
	created_by varchar(255),
	
	PRIMARY KEY (id)
);