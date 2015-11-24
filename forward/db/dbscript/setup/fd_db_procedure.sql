/**********************************************************
Create procedure for forward database
**********************************************************/
use fddb;

/***
Create procedure for refresh fans message count by month
*/
DELIMITER $$
DROP PROCEDURE IF EXISTS fd_p_refreshfansmessagecount;
CREATE PROCEDURE fd_p_refreshfansmessagecount()
BEGIN
	UPDATE fd_t_fansmessageconfig 
    SET current_p2p_count = next_p2p_count, 
    p2p_remain_count = next_p2p_count, 
    current_mass_count = next_mass_count, 
    mass_remain_count = next_mass_count;
END;
$$

/***
Create procedure for refresh fans message count by month
*/
DELIMITER $$
DROP PROCEDURE IF EXISTS fd_p_refreshservicestatus;
CREATE PROCEDURE fd_p_refreshservicestatus()
BEGIN
	UPDATE fd_t_shopaccount
    SET
    service_status = 5
    WHERE
    service_deadline <= now();
END;
$$

DELIMITER ;