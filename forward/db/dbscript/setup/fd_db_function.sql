/**********************************************************
Create functions for forward database
**********************************************************/
use fddb;

/*Get sequence current value function*/
DELIMITER $ 
DROP FUNCTION IF EXISTS `fd_func_currentvalue`;
CREATE FUNCTION `fd_func_currentvalue`(seq_name VARCHAR(64)) RETURNS BIGINT(20)
BEGIN
  DECLARE value BIGINT;

  SET value = 0;
  SELECT current_value
  INTO
    value
  FROM
    fd_t_sequence
  WHERE
    sequence_name = seq_name;
  RETURN value;
END$
DELIMITER ; 

/*Set sequence current value function*/
DELIMITER $ 
DROP FUNCTION IF EXISTS `fd_func_setvalue`;
CREATE FUNCTION `fd_func_setvalue`(seq_name VARCHAR(64), seq_value BIGINT(20)) RETURNS BIGINT(20)
BEGIN
  UPDATE fd_t_sequence
  SET
    current_value = seq_value
  WHERE
    sequence_name = seq_name;
  RETURN fd_func_currentvalue(seq_name);
END$
DELIMITER ; 

/*Get sequence next value function*/
DELIMITER $ 
DROP FUNCTION IF EXISTS `fd_func_nextvalue`;
CREATE FUNCTION `fd_func_nextvalue`(seq_name VARCHAR(64)) RETURNS BIGINT(20)
BEGIN
  UPDATE fd_t_sequence
  SET
    current_value = current_value + increment_value
  WHERE
    sequence_name = seq_name;
  RETURN fd_func_currentvalue(seq_name);
END$
DELIMITER ; 