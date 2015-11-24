/*Clean virtual table data*/
delete from fd_t_shop;
delete from fd_t_shopaccount;
delete from fd_t_shopchargedetail;
delete from fd_t_user;
delete from fd_t_account;
delete from fd_t_useraddress;
delete from fd_t_goods;
delete from fd_t_goodsstandard;
delete from fd_t_fitting;
delete from fd_t_activity;
delete from fd_t_recommend;
delete from fd_t_phoneauth;
delete from fd_t_favorite;
delete from fd_t_fans;
delete from fd_t_visitedshop;
delete from fd_t_friend;
delete from fd_t_privatesetting;
delete from fd_t_fansmessage;
delete from fd_t_forum;
delete from fd_t_feedback;
delete from fd_t_appversion;
delete from fd_t_userlogindevice;
delete from fd_t_systemmessage;
delete from fd_t_visitshoprecord;
delete from fd_t_fansmessageconfig;
delete from fd_t_joinshop;
delete from fd_t_goodsinfo;
delete from fd_t_bill_201501;
delete from fd_t_userbill_1;
delete from fd_t_shopbill_1;
delete from fd_t_commission;

/*Clean virtual table data*/
update fd_t_sequence set current_value = 10000 where sequence_name = 'FD_ACCOUNT_ID';
update fd_t_sequence set current_value = 1 where sequence_name = 'FD_ADDRESS_ID';
update fd_t_sequence set current_value = 1 where sequence_name = 'FD_GOODS_ID';
update fd_t_sequence set current_value = 1 where sequence_name = 'FD_SHOP_IMAGE_ID';
