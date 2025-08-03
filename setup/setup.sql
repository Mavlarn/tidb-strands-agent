
-- 电商客户服务场景模拟数据
DROP DATABASE IF EXISTS `cs_demo_db`;
CREATE DATABASE `cs_demo_db`;

USE cs_demo_db;
    
-- 电商客户服务场景模拟数据

-- 1. 商品表
CREATE TABLE `products` (
    `product_id` VARCHAR(255),
    `product_name` VARCHAR(255),
    `category` VARCHAR(255) COMMENT '商品类型',
    `price` FLOAT COMMENT '商品价格',
    `stock_quantity` INT,
    `brand` VARCHAR(255)
  );

INSERT INTO products VALUES
('P001', 'ZenPhone Pro 256GB', '智能手机', 8999.00, 50, 'TechZen'),
('P002', 'FlashMobile Ultra 512GB', '智能手机', 5999.00, 30, 'FlashTech'),
('P003', 'TabletMax Pro 12.9寸', '平板电脑', 8999.00, 100, 'TechZen'),
('P004', 'SmartPad Elite', '平板电脑', 4999.00, 80, 'DigitalWave'),
('P005', 'SoundBuds Pro 2', '蓝牙耳机', 1899.00, 25, 'TechZen'),
('P006', 'AudioMax WX-2000', '蓝牙耳机', 2399.00, 200, 'AudioMax'),
('P007', 'PowerBook Pro 14寸', '笔记本电脑', 15999.00, 20, 'TechZen'),
('P008', 'BusinessLaptop X1', '笔记本电脑', 12999.00, 15, 'ProTech');

-- 2. 订单表
CREATE TABLE `orders` (
    `order_id` VARCHAR(255),
    `customer_id` VARCHAR(255),
    `product_id` VARCHAR(255),
    `quantity` INTEGER,
    `total_amount` FLOAT COMMENT '订单金额',
    `order_status` VARCHAR(255) COMMENT '订单的状态，包括正常状态如已完成，以及各种异常状态，如已换货、已退货等，以及中间状态，有已发货、换货中、退款中等',
    `order_date` TIMESTAMP,
    `customer_name` VARCHAR(255),
    `customer_phone` VARCHAR(255),
    `shipping_address` VARCHAR(255)
  );

INSERT INTO orders VALUES
('O001', 'C001', 'P001', 1, 8999.00, '已完成', '2024-01-15 10:30:00', '张三', '13800138001', '北京市朝阳区建国路1号'),
('O002', 'C002', 'P003', 2, 17998.00, '已取消', '2024-01-16 14:20:00', '李四', '13800138002', '上海市浦东新区陆家嘴路100号'),
('O003', 'C003', 'P005', 1, 1899.00, '已退货', '2024-01-18 09:15:00', '王五', '13800138003', '广州市天河区珠江路200号'),
('O004', 'C004', 'P007', 1, 15999.00, '已换货', '2024-01-20 16:45:00', '赵六', '13800138004', '深圳市南山区科技园300号'),
('O005', 'C005', 'P002', 1, 5999.00, '已发货', '2024-01-22 11:30:00', '钱七', '13800138005', '杭州市西湖区文三路400号'),
('O006', 'C006', 'P004', 1, 4999.00, '已完成', '2024-01-25 13:20:00', '孙八', '13800138006', '成都市锦江区春熙路500号'),
('O007', 'C007', 'P006', 1, 2399.00, '退款中', '2024-01-28 15:10:00', '周九', '13800138007', '武汉市武昌区中南路600号'),
('O008', 'C001', 'P008', 1, 12999.00, '已完成', '2024-02-01 08:45:00', '张三', '13800138001', '北京市朝阳区建国路1号'),
('O009', 'C008', 'P001', 1, 8999.00, '已发货', '2024-02-03 14:20:00', '吴十', '13800138008', '西安市雁塔区高新路700号'),
('O010', 'C009', 'P005', 2, 3798.00, '已完成', '2024-02-05 09:30:00', '郑十一', '13800138009', '南京市鼓楼区中山路800号'),
('O011', 'C010', 'P002', 1, 5999.00, '已退货', '2024-02-07 16:15:00', '王十二', '13800138010', '天津市和平区南京路900号'),
('O012', 'C011', 'P007', 1, 15999.00, '已完成', '2024-02-10 11:45:00', '李十三', '13800138011', '重庆市渝中区解放碑1000号'),
('O013', 'C012', 'P003', 1, 8999.00, '已换货', '2024-02-12 13:30:00', '张十四', '13800138012', '青岛市市南区香港路1100号'),
('O014', 'C013', 'P006', 2, 4798.00, '已完成', '2024-02-15 10:20:00', '陈十五', '13800138013', '大连市中山区人民路1200号'),
('O015', 'C014', 'P008', 1, 12999.00, '退款中', '2024-02-18 15:40:00', '刘十六', '13800138014', '苏州市姑苏区观前街1300号'),
('O016', 'C015', 'P004', 1, 4999.00, '已发货', '2024-02-20 08:50:00', '黄十七', '13800138015', '厦门市思明区中山路1400号');

-- 3. 物流表
CREATE TABLE `logistics` (
    `logistics_id` VARCHAR(255),
    `order_id` VARCHAR(255),
    `logistics_company` VARCHAR(255),
    `tracking_number` VARCHAR(255),
    `logistics_status` VARCHAR(255),
    `shipped_date` TIMESTAMP,
    `delivered_date` TIMESTAMP,
    `current_location` VARCHAR(255)
  );

INSERT INTO logistics VALUES
('L001', 'O001', '顺丰速运', 'SF1234567890', '已签收', '2024-01-16 08:00:00', '2024-01-17 14:30:00', '北京市朝阳区'),
('L002', 'O002', '圆通速递', 'YT9876543210', '已取消', '2024-01-16 15:00:00', NULL, '上海分拣中心'),
('L003', 'O003', '中通快递', 'ZT5555666677', '退货运输中', '2024-01-19 10:00:00', NULL, '广州转运中心'),
('L004', 'O004', '韵达快递', 'YD1111222233', '换货运输中', '2024-01-21 09:30:00', NULL, '深圳分拣中心'),
('L005', 'O005', '申通快递', 'ST7777888899', '运输中', '2024-01-23 07:45:00', NULL, '杭州转运中心'),
('L006', 'O006', '顺丰速运', 'SF2468135790', '已签收', '2024-01-26 09:15:00', '2024-01-27 16:20:00', '成都市锦江区'),
('L007', 'O007', '京东物流', 'JD3691472580', '退货中', '2024-01-29 11:00:00', NULL, '武汉分拣中心'),
('L008', 'O008', '顺丰速运', 'SF9517534680', '已签收', '2024-02-02 08:30:00', '2024-02-03 15:45:00', '北京市朝阳区'),
('L009', 'O009', '中通快递', 'ZT8888999900', '运输中', '2024-02-04 10:15:00', NULL, '西安转运中心'),
('L010', 'O010', '韵达快递', 'YD2222333344', '已签收', '2024-02-06 08:20:00', '2024-02-07 16:30:00', '南京市鼓楼区'),
('L011', 'O011', '申通快递', 'ST4444555566', '退货运输中', '2024-02-08 14:45:00', NULL, '天津转运中心'),
('L012', 'O012', '顺丰速运', 'SF6666777788', '已签收', '2024-02-11 09:30:00', '2024-02-12 14:20:00', '重庆市渝中区'),
('L013', 'O013', '京东物流', 'JD9999000011', '换货运输中', '2024-02-13 11:15:00', NULL, '青岛分拣中心'),
('L014', 'O014', '圆通速递', 'YT1111222233', '已签收', '2024-02-16 08:40:00', '2024-02-17 15:50:00', '大连市中山区'),
('L015', 'O015', '中通快递', 'ZT3333444455', '退货中', '2024-02-19 13:25:00', NULL, '苏州分拣中心'),
('L016', 'O016', '韵达快递', 'YD5555666677', '运输中', '2024-02-21 07:30:00', NULL, '厦门转运中心');

-- 4. 商品评论表
-- DROP TABLE if EXISTS product_reviews;
CREATE TABLE `product_reviews` (
    `review_id` VARCHAR(255) PRIMARY KEY,
    `order_id` VARCHAR(255),
    `product_id` VARCHAR(255),
    `customer_id` VARCHAR(255),
    `rating` INTEGER,
    `product_name` VARCHAR(255),
    `review_content` TEXT COMMENT '评论内容',
    `review_content_vec` VECTOR(1024) COMMENT '向量化的评论内容',
    `review_date` VARCHAR(255),
    `is_verified_purchase` BOOLEAN
  );

-- 5. 客服记录表
-- DROP TABLE if EXISTS customer_service_records;
CREATE TABLE `customer_service_records` (
    `record_id` VARCHAR(255) NOT NULL PRIMARY KEY,
    `order_id` VARCHAR(255) NOT NULL,
    `customer_id` VARCHAR(255) NOT NULL,
    `service_type` VARCHAR(255) NOT NULL COMMENT '客户申请的售后服务类型，如申请退货或换货、物流咨询等',
    `issue_category` VARCHAR(255) NOT NULL COMMENT '客户申请的售后服务的原因，例如产品质量问题、配送问题等',
    `conversation_log` TEXT NOT NULL COMMENT '客服沟通记录',
    `conversation_log_vec` VECTOR(1024) COMMENT '向量化的客服沟通记录',
    `service_agent` VARCHAR(255) NOT NULL,
    `created_date` VARCHAR(255),
    `resolved_date` VARCHAR(255) NULL,
    `resolution_status` VARCHAR(255) NOT NULL COMMENT '客服解决的结果',
    `product_name` VARCHAR(255)
  );

SELECT 'Data insertion completed successfully' as status;

-- 查询示例
select count(*) from product_reviews;
select count(*) from customer_service_records;
