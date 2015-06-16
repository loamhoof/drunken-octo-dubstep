# drunken-octo-dubstep
Reproduce an SQLAlchemy problem stemming from the concurrent use of both bulk_insert_mappings and bulk_update_mappings thanks to greenlets.

## What can be seen
When running both a `bulk_insert_mapping` and a `bulk_update_mapping` concurrently on the same `session` object, the following rule must be followed concerning the first mapping sent to either function:
* if it was sent to the `bulk_insert`, the `bulk_update` has to finish first
* if it was sent to the `bulk_update`, the `bulk_insert` has to finish first

More details inside the `drunken-octo-dubsteo.py` file.

## How to run the project
### With docker & docker-compose
```
# Start by running the containers
docker-compose run --rm script bash
# In another shell, prepare the db
docker exec -it drunkenoctodubstep_db_1 bash
psql -Upostgres < fixture.sql
# Back to the first shell, run the script
python drunken-octo-dubstep.py
# This will print
> Start with an insert first.
> And end the bulk_insert first.
> This does not work.
> Start with an insert first.
> But end with the bulk_update first.
> And it works.
> Start with an insert, do a bunch of things, end with an insert.
> Still works, what counts is the first operation.
```
