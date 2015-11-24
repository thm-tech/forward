/**********************************************************
Create event for forward database
**********************************************************/
use fddb;

/***
Create event for update shop fans message count
*/
DELIMITER $$
CREATE EVENT IF NOT EXISTS fd_e_refreshfansmessagecount
ON SCHEDULE EVERY 1 MONTH STARTS '2015-01-01 00:00:00'
ON COMPLETION PRESERVE ENABLE
COMMENT 'Refresh shop fans message count by month'
DO CALL fd_p_refreshfansmessagecount;
$$

/***
Create event for update shop service status
*/
DELIMITER $$
CREATE EVENT IF NOT EXISTS fd_e_refreshservicestatus
ON SCHEDULE EVERY 1 DAY STARTS '2015-01-01 00:00:00'
ON COMPLETION PRESERVE ENABLE
COMMENT 'Refresh shop service status by day'
DO CALL fd_p_refreshservicestatus;
$$

DELIMITER ;

