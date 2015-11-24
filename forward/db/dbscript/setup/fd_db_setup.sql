/**********************************************************
Initialise database for forward platform
**********************************************************/

/***
Enable event scheduler
*/
SET @@global.event_scheduler = ON;

/***
Create database and user
*/
CREATE database IF NOT EXISTS fddb;
GRANT ALL PRIVILEGES ON fddb.* TO fd@'localhost' IDENTIFIED BY "bEijingyinpu_2015";
GRANT EVENT ON fddb.* TO fd@'%';
flush PRIVILEGES;
use fddb;

/***
Create tables
*/
SOURCE fd_db_table.sql;

/***
Create functions
*/
SOURCE fd_db_function.sql;

/***
Create procedures
*/
SOURCE fd_db_procedure.sql;

/***
Create jobs
*/
SET GLOBAL event_scheduler = ON;  
SOURCE fd_db_job.sql;

/***
Initialise data
*/
SOURCE fd_db_initdata.sql;
SOURCE fd_db_initcity.sql;

/***
Initialise test data
*/



