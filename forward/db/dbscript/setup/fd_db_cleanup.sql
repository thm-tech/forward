use fddb;

/***
Drop tables
*/


/***
Drop sequences
*/
DROP TABLE IF EXISTS `fd_t_sequence`;

/***
Drop functions
*/
DROP FUNCTION IF EXISTS `fd_func_currentvalue`;
DROP FUNCTION IF EXISTS `fd_func_setvalue`;
DROP FUNCTION IF EXISTS `fd_func_nextvalue`;

/***
Drop jobs
*/
DROP EVENT IF EXISTS fd_e_refreshfansmessagecount;
DROP EVENT IF EXISTS fd_e_refreshservicestatus;

/***
Drop procedures
*/
DROP PROCEDURE IF EXISTS fd_p_refreshfansmessagecount;
DROP PROCEDURE IF EXISTS fd_p_refreshservicestatus;

/***
Drop database and user
*/
DROP user fd@'%';
DROP user fd@'localhost';
DROP database IF EXISTS fddb;
