CREATE TABLE billing_log (
	id int NOT NULL AUTO_INCREMENT,
	cust_acc_id int NOT NULL,
	period_month int,
	period_year int,
	inv_date DATE,
	due_date DATE,
	total_amount int,
	
	created_at timestamp default current_timestamp(),
	created_by varchar(255),
	updated_at timestamp default current_timestamp(),
	updated_by varchar(255),
	
	PRIMARY KEY (id),
	FOREIGN KEY (cust_acc_id) REFERENCES myrep_cust_account(id)
);
