/**********************************************************
Initialise data for forward database
**********************************************************/
use fddb;

/*Initialise sequence data*/
INSERT INTO `fd_t_sequence` VALUES ('FD_ACCOUNT_ID', 10000, 1);
INSERT INTO `fd_t_sequence` VALUES ('FD_ADDRESS_ID', 1, 1);
INSERT INTO `fd_t_sequence` VALUES ('FD_GOODS_ID', 1, 1);
INSERT INTO `fd_t_sequence` VALUES ('FD_SHOP_IMAGE_ID', 1, 1);
INSERT INTO `fd_t_sequence` VALUES ('FD_SHARE_ID', 1, 1);
INSERT INTO `fd_t_sequence` VALUES ('FD_TAG_ID', 1, 1);

/*Initialise category*/
INSERT INTO `fd_t_category`  VALUES (100, '服装鞋帽', null, '', null),
                                    (101, '女装', 100, '', null),
                                    (102, '男装', 100, '', null),
                                    (103, '童装', 100, '', null),
                                    (104, '内衣', 100, '', null),
                                    (105, '袜子', 100, '', null),									
									(106, '女鞋', 100, '', null),
									(107, '男鞋', 100, '', null),
                                    (108, '童鞋', 100, '', null),
									(109, '户外鞋服', 100, '', null),
									(110, '帽子', 100, '', null),
									(199, '其他', 100, '', null);
									
INSERT INTO `fd_t_category`  VALUES (200, '美食', null, '', null),
                                    (201, '甜品饮品', 200, '', null),
                                    (202, '自助餐', 200, '', null),
                                    (203, '火锅', 200, '', null),
									(204, '小吃快餐', 200, '', null),
									(205, '川湘菜', 200, '', null),
									(206, '徽菜', 200, '', null),
									(207, '烧烤烤肉', 200, '', null),
									(208, '咖啡酒吧', 200, '', null),
									(209, '西餐', 200, '', null),
									(210, '江浙菜', 200, '', null),
									(211, '西北菜', 200, '', null),
									(212, '粤菜', 200, '', null),
									(213, '鲁菜', 200, '', null),
									(214, '东北菜', 200, '', null),
									(215, '云贵菜', 200, '', null),
									(216, '日韩料理', 200, '', null),
									(217, '海鲜', 200, '', null),
                                    (218, '休闲零食', 200, '', null),
									(219, '烤鱼', 200, '', null),
									(220, '面点米粉凉皮', 200, '', null),
									(221, '主题餐厅', 200, '', null),
									(299, '其他', 200, '', null);
									
INSERT INTO `fd_t_category`  VALUES (300, '休闲娱乐', null, '', null),
                                    (301, '足疗按摩', 300, '', null),
                                    (302, '儿童乐园', 300, '', null),
                                    (303, '桌游电玩', 300, '', null),
                                    (304, '运动健身', 300, '', null),
									(305, '电影', 300, '', null),
									(306, 'KTV', 300, '', null),
									(307, '洗浴汗蒸', 300, '', null),
									(308, '温泉', 300, '', null),
									(399, '其他', 300, '', null);
									
INSERT INTO `fd_t_category`  VALUES (400, '箱包皮具', null, '', null),
                                    (401, '时尚女包', 400, '', null),
                                    (402, '精品男包', 400, '', null),
                                    (403, '旅行箱包', 400, '', null),
                                    (404, '皮具', 400, '', null),
									(499, '其他', 400, '', null);

INSERT INTO `fd_t_category`  VALUES (500, '手表眼镜', null, '', null),
                                    (501, '手表', 500, '', null),
                                    (502, '眼镜', 500, '', null),
									(599, '其他', 500, '', null);

INSERT INTO `fd_t_category`  VALUES (600, '丽人', null, '', null),
                                    (601, '美甲', 600, '', null),
                                    (602, '美发', 600, '', null),
                                    (603, '个护化妆', 600, '', null),
									(604, '美容SPA', 600, '', null),
									(699, '其他', 600, '', null);
									
INSERT INTO `fd_t_category`  VALUES (700, '珠宝饰品', null, '', null),
                                    (701, '黄金铂金', 700, '', null),
                                    (702, '钻石', 700, '', null),
                                    (703, '翡翠玉石', 700, '', null),
                                    (704, '水晶玛瑙', 700, '', null),
                                    (705, '银饰', 700, '', null),
                                    (706, '时尚饰品', 700, '', null),
									(707, '工艺品', 700, '', null),
									(799, '其他', 700, '', null);
									
INSERT INTO `fd_t_category`  VALUES (800, '家居绿植', null, '', null),
									(801, '家居', 800, '', null),
									(802, '绿植', 800, '', null),
									(803, '花艺', 800, '', null),
									(899, '其他', 800, '', null);







