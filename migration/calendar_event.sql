
CREATE TABLE myrep_calendar_event (
	id int NOT NULL AUTO_INCREMENT,
	event_id varchar(255) NOT NULL,
	bill_log_id int NOT NULL,
	
	created_at timestamp default current_timestamp(),
	created_by varchar(255),
	
	PRIMARY KEY (id),
	FOREIGN KEY (bill_log_id) REFERENCES myrep_billing_log(id)
);