CREATE TABLE payment_log (
	id int NOT NULL AUTO_INCREMENT,
	cust_acc_id int NOT NULL,
	period_month int,
	period_year int,
	payment_date DATE,
	total_amount int,
	bill_log_id int,
	
	created_at timestamp default current_timestamp(),
	created_by varchar(255),
	
	PRIMARY KEY (id),
	FOREIGN KEY (bill_log_id) REFERENCES myrep_billing_log(id),
	FOREIGN KEY (cust_acc_id) REFERENCES myrep_cust_account(id)
);