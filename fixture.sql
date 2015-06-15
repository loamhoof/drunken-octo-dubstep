CREATE TABLE test_model (
	id	integer CONSTRAINT test_model_pk PRIMARY KEY,
    value	varchar(40) NOT NULL
);

INSERT INTO test_model VALUES (1, 1);
