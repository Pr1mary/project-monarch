CREATE TABLE cust_account (
	id int NOT NULL AUTO_INCREMENT,
	cust_id varchar(255),
	
	created_at timestamp default current_timestamp(),
	created_by varchar(255),
	
	PRIMARY KEY (id)
);
