-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: jewellery_erp
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('b3b75aaeac27');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `entity_name` varchar(100) NOT NULL,
  `entity_id` varchar(100) NOT NULL,
  `action` varchar(50) NOT NULL,
  `changes` json DEFAULT NULL,
  `timestamp` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_audit_logs_entity_name` (`entity_name`),
  KEY `ix_audit_logs_timestamp` (`timestamp`),
  KEY `ix_audit_logs_entity_id` (`entity_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bill_items`
--

DROP TABLE IF EXISTS `bill_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_id` int NOT NULL,
  `inventory_id` int DEFAULT NULL,
  `item_name` varchar(100) NOT NULL,
  `metal_type` varchar(20) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `rate` decimal(12,2) NOT NULL,
  `making_charge` decimal(12,2) DEFAULT NULL,
  `making_charge_type` varchar(20) DEFAULT NULL,
  `hallmark_charge` decimal(12,2) DEFAULT NULL,
  `other_charges` decimal(12,2) DEFAULT NULL,
  `total` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  KEY `inventory_id` (`inventory_id`),
  KEY `ix_bill_items_id` (`id`),
  CONSTRAINT `bill_items_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `bills` (`id`),
  CONSTRAINT `bill_items_ibfk_2` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill_items`
--

LOCK TABLES `bill_items` WRITE;
/*!40000 ALTER TABLE `bill_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `bill_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bills`
--

DROP TABLE IF EXISTS `bills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bills` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) NOT NULL,
  `customer_id` int NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `discount` decimal(12,2) DEFAULT NULL,
  `cgst` decimal(12,2) DEFAULT NULL,
  `sgst` decimal(12,2) DEFAULT NULL,
  `igst` decimal(12,2) DEFAULT NULL,
  `round_off` decimal(5,2) DEFAULT NULL,
  `grand_total` decimal(12,2) NOT NULL,
  `payment_status` enum('PENDING','PARTIAL','COMPLETED') DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_bills_invoice_number` (`invoice_number`),
  KEY `customer_id` (`customer_id`),
  KEY `ix_bills_id` (`id`),
  CONSTRAINT `bills_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bills`
--

LOCK TABLES `bills` WRITE;
/*!40000 ALTER TABLE `bills` DISABLE KEYS */;
/*!40000 ALTER TABLE `bills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `metal_type` enum('GOLD','SILVER') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_categories_name` (`name`),
  KEY `ix_categories_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=174 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_addresses`
--

DROP TABLE IF EXISTS `customer_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_addresses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `address_line1` text NOT NULL,
  `address_line2` text,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `zip_code` varchar(20) NOT NULL,
  `is_default` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_customer_addresses_customer_id` (`customer_id`),
  CONSTRAINT `customer_addresses_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_addresses`
--

LOCK TABLES `customer_addresses` WRITE;
/*!40000 ALTER TABLE `customer_addresses` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_ledgers`
--

DROP TABLE IF EXISTS `customer_ledgers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_ledgers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `date` datetime NOT NULL,
  `voucher_type` varchar(50) NOT NULL,
  `voucher_number` varchar(50) DEFAULT NULL,
  `description` text,
  `debit` decimal(12,2) NOT NULL,
  `credit` decimal(12,2) NOT NULL,
  `balance` decimal(12,2) NOT NULL,
  `gold_debit` decimal(10,3) NOT NULL,
  `gold_credit` decimal(10,3) NOT NULL,
  `gold_balance` decimal(10,3) NOT NULL,
  `silver_debit` decimal(10,3) NOT NULL,
  `silver_credit` decimal(10,3) NOT NULL,
  `silver_balance` decimal(10,3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_customer_ledgers_customer_id` (`customer_id`),
  CONSTRAINT `customer_ledgers_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_ledgers`
--

LOCK TABLES `customer_ledgers` WRITE;
/*!40000 ALTER TABLE `customer_ledgers` DISABLE KEYS */;
INSERT INTO `customer_ledgers` VALUES (1,104,'2026-07-31 16:01:16','Exchange','EXC-1','Exchange Difference Settlement',0.00,657005.58,-651313.58,0.000,0.000,0.000,0.000,0.000,0.000),(2,105,'2026-08-01 06:59:22','Exchange','EXC-2','Exchange Difference Settlement',0.00,13926.86,-11232.86,0.000,0.000,0.000,0.000,0.000,0.000),(3,116,'2026-08-01 18:35:30','Exchange','EXC-3','Exchange Difference Settlement',746235.00,0.00,746235.00,0.000,0.000,0.000,0.000,0.000,0.000),(4,118,'2026-08-01 19:35:54','Exchange','EXC-4','Exchange Difference Settlement',7396694.78,0.00,7396694.78,0.000,0.000,0.000,0.000,0.000,0.000),(5,118,'2026-08-01 19:41:06','Payment','','10000',100000.00,0.00,7496694.78,0.000,0.000,0.000,0.000,0.000,0.000),(6,118,'2026-08-01 19:41:27','Payment','','100',0.00,18888888.00,-11392193.22,0.000,0.000,0.000,0.000,0.000,0.000),(7,116,'2026-08-01 19:46:00','Exchange','EXC-5','Exchange Difference Settlement',0.00,66364.20,679870.80,0.000,0.000,0.000,0.000,0.000,0.000),(8,116,'2026-08-01 19:48:50','Exchange','EXC-6','Exchange Difference Settlement',0.00,730006.20,-50135.40,0.000,0.000,0.000,0.000,0.000,0.000),(9,118,'2026-08-02 03:16:49','Manual','','',0.00,0.00,-11392193.22,110.000,110.000,0.000,0.000,0.000,0.000),(10,120,'2026-08-02 04:27:26','Exchange','EXC-7','Exchange Difference Settlement',178690.50,0.00,178690.50,0.000,0.000,0.000,0.000,0.000,0.000),(11,120,'2026-08-02 04:27:26','Payment','PAY-EXC-7','Payment for Exchange EXC-7',0.00,100000.50,78690.00,0.000,0.000,0.000,0.000,0.000,0.000),(12,116,'2026-08-02 05:45:35','Invoice','INV-20260802-0009','Sales Bill INV-20260802-0009',10197.00,0.00,-39938.40,0.000,0.000,0.000,0.000,0.000,0.000),(13,116,'2026-08-02 05:45:35','Payment','INV-20260802-0009','Payment for INV-20260802-0009',0.00,5197.00,-45135.40,0.000,0.000,0.000,0.000,0.000,0.000),(14,116,'2026-08-02 05:55:12','Exchange','EXC-8','Exchange Difference Settlement',1672.29,0.00,-43463.11,0.000,0.000,0.000,0.000,0.000,0.000),(15,116,'2026-08-02 05:55:12','Payment','PAY-EXC-8','Payment for Exchange EXC-8',0.00,1000.29,-44463.40,0.000,0.000,0.000,0.000,0.000,0.000),(16,116,'2026-08-02 06:01:21','Invoice','INV-20260802-0024','Sales Bill INV-20260802-0024',21609.00,0.00,-22854.40,0.000,0.000,0.000,0.000,0.000,0.000),(17,116,'2026-08-02 06:01:21','Payment','INV-20260802-0024','Payment for INV-20260802-0024',0.00,5000.00,-27854.40,0.000,0.000,0.000,0.000,0.000,0.000),(18,89,'2026-08-02 06:02:27','Invoice','INV-20260802-0025','Sales Bill INV-20260802-0025',11412.00,0.00,18122.00,0.000,0.000,0.000,0.000,0.000,0.000),(19,89,'2026-08-02 06:02:27','Payment','INV-20260802-0025','Payment for INV-20260802-0025',0.00,6000.00,12122.00,0.000,0.000,0.000,0.000,0.000,0.000),(20,116,'2026-08-02 07:21:15','Exchange','EXC-9','Exchange Difference Settlement',10225.34,0.00,-17629.06,0.000,0.000,0.000,0.000,0.000,0.000),(21,116,'2026-08-02 07:21:15','Payment','PAY-EXC-9','Payment for Exchange EXC-9',0.00,225.34,-17854.40,0.000,0.000,0.000,0.000,0.000,0.000),(22,116,'2026-08-02 07:26:37','Invoice','INV-20260802-0026','Sales Bill INV-20260802-0026',230143.00,0.00,212288.60,0.000,0.000,0.000,0.000,0.000,0.000),(23,116,'2026-08-02 07:26:37','Payment','INV-20260802-0026','Payment for INV-20260802-0026',0.00,200000.00,12288.60,0.000,0.000,0.000,0.000,0.000,0.000),(24,116,'2026-08-02 07:27:25','Invoice','INV-20260802-0027','Sales Bill INV-20260802-0027',27060.00,0.00,39348.60,0.000,0.000,0.000,0.000,0.000,0.000),(25,116,'2026-08-02 07:27:25','Payment','INV-20260802-0027','Payment for INV-20260802-0027',0.00,2788.00,36560.60,0.000,0.000,0.000,0.000,0.000,0.000),(26,116,'2026-08-02 07:29:38','Exchange','EXC-10','Exchange Difference Settlement',1187.89,0.00,37748.49,0.000,0.000,0.000,0.000,0.000,0.000),(27,116,'2026-08-02 07:29:38','Payment','PAY-EXC-10','Payment for Exchange EXC-10',0.00,187.00,37561.49,0.000,0.000,0.000,0.000,0.000,0.000),(28,120,'2026-08-02 07:45:31','Invoice','INV-20260802-0028','Sales Bill INV-20260802-0028',67203.00,0.00,145893.00,0.000,0.000,0.000,0.000,0.000,0.000),(29,120,'2026-08-02 07:45:31','Payment','INV-20260802-0028','Payment for INV-20260802-0028',0.00,60000.00,85893.00,0.000,0.000,0.000,0.000,0.000,0.000),(30,119,'2026-08-02 07:46:03','Invoice','INV-20260802-0029','Sales Bill INV-20260802-0029',6719.00,0.00,6719.00,0.000,0.000,0.000,0.000,0.000,0.000),(31,119,'2026-08-02 07:46:03','Payment','INV-20260802-0029','Payment for INV-20260802-0029',0.00,78.00,6641.00,0.000,0.000,0.000,0.000,0.000,0.000),(32,116,'2026-08-02 07:49:22','Invoice','INV-20260802-0030','Sales Bill INV-20260802-0030',65246.00,0.00,102807.49,0.000,0.000,0.000,0.000,0.000,0.000),(33,116,'2026-08-02 07:49:22','Payment','INV-20260802-0030','Payment for INV-20260802-0030',0.00,6524.00,96283.49,0.000,0.000,0.000,0.000,0.000,0.000),(34,116,'2026-08-02 08:29:11','Invoice','INV-20260802-0031','Sales Bill INV-20260802-0031',6719.00,0.00,103002.49,0.000,0.000,0.000,0.000,0.000,0.000),(35,116,'2026-08-02 08:29:11','Payment','INV-20260802-0031','Payment for INV-20260802-0031',0.00,1000.00,102002.49,0.000,0.000,0.000,0.000,0.000,0.000),(36,116,'2026-08-02 08:56:49','Invoice','INV-20260802-0032','Sales Bill INV-20260802-0032',7045.00,0.00,109047.49,0.000,0.000,0.000,0.000,0.000,0.000),(37,116,'2026-08-02 08:56:49','Payment','INV-20260802-0032','Payment for INV-20260802-0032',0.00,7000.00,102047.49,0.000,0.000,0.000,0.000,0.000,0.000);
/*!40000 ALTER TABLE `customer_ledgers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL,
  `aadhaar_pan` varchar(50) DEFAULT NULL,
  `credit_limit` decimal(12,2) DEFAULT NULL,
  `outstanding_balance` decimal(12,2) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `fine_gold_balance` decimal(10,3) DEFAULT NULL,
  `fine_silver_balance` decimal(10,3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_customers_phone_number` (`phone_number`),
  UNIQUE KEY `ix_customers_email` (`email`),
  KEY `ix_customers_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (50,'Cust_fm7I2d',NULL,'5751836621',NULL,NULL,'Mumbai',NULL,NULL,'154826180016',0.00,2134.00,1,'2026-07-31 19:40:13',NULL,0,NULL,NULL),(51,'Cust_y4ZRCj',NULL,'2925986483',NULL,NULL,'Mumbai',NULL,NULL,'803913686701',0.00,8014.00,1,'2026-07-31 19:40:13',NULL,0,NULL,NULL),(52,'Cust_8uzC3k',NULL,'3118604943',NULL,NULL,'Mumbai',NULL,NULL,'344897899994',0.00,9310.00,1,'2026-07-31 19:40:14',NULL,0,NULL,NULL),(53,'Cust_Xi5W4q',NULL,'9914599742',NULL,NULL,'Pune',NULL,NULL,'578196139253',0.00,8938.00,1,'2026-07-31 19:40:14','2026-07-31 19:40:15',0,NULL,NULL),(55,'Cust_KWcB3n',NULL,'1972811083',NULL,NULL,'Mumbai',NULL,NULL,'644537213923',0.00,9633.00,1,'2026-07-31 19:47:44',NULL,0,NULL,NULL),(56,'Cust_3p0Qmh',NULL,'9220397992',NULL,NULL,'Mumbai',NULL,NULL,'549547469311',0.00,3771.00,1,'2026-07-31 19:47:45',NULL,0,NULL,NULL),(57,'Cust_AxKd3E',NULL,'5982663971',NULL,NULL,'Mumbai',NULL,NULL,'877179110296',0.00,6478.00,1,'2026-07-31 19:47:48',NULL,0,NULL,NULL),(58,'Cust_T1nvkh',NULL,'7132030385',NULL,NULL,'Pune',NULL,NULL,'208837095278',0.00,2600.00,1,'2026-07-31 19:47:48','2026-07-31 19:47:49',0,NULL,NULL),(60,'Cust_WA0JIo',NULL,'9300226995',NULL,NULL,'Pune',NULL,NULL,'197016396068',0.00,2684.00,1,'2026-07-31 20:00:23','2026-07-31 20:00:24',0,NULL,NULL),(61,'Cust_KDAmpf',NULL,'2672341329',NULL,NULL,'Mumbai',NULL,NULL,'338545061836',0.00,350.00,1,'2026-07-31 20:00:23',NULL,0,NULL,NULL),(62,'Cust_LB01A7',NULL,'2292619604',NULL,NULL,'Mumbai',NULL,NULL,'343363984894',0.00,1415.00,1,'2026-07-31 20:00:24',NULL,0,NULL,NULL),(63,'Cust_LnIlWd',NULL,'4882348191',NULL,NULL,'Mumbai',NULL,NULL,'718978564051',0.00,4486.00,1,'2026-07-31 20:00:25',NULL,0,NULL,NULL),(86,'Cust_eqyYgX',NULL,'5753104175',NULL,NULL,'Mumbai',NULL,NULL,'571296923743',0.00,9107.00,1,'2026-07-31 20:59:20',NULL,0,NULL,NULL),(87,'Cust_pf8DXC',NULL,'7461915713',NULL,NULL,'Pune',NULL,NULL,'769918105351',0.00,9074.00,1,'2026-07-31 20:59:22','2026-07-31 20:59:24',0,NULL,NULL),(88,'Cust_VwQJlG',NULL,'7690030649',NULL,NULL,'Mumbai',NULL,NULL,'203043542260',0.00,1320.00,1,'2026-07-31 20:59:22',NULL,0,NULL,NULL),(89,'Cust_Gdb8vU',NULL,'4026877734',NULL,NULL,'Mumbai',NULL,NULL,'616994855368',0.00,12122.00,1,'2026-07-31 20:59:23','2026-08-02 11:32:26',0,NULL,NULL),(99,'Cust_QQUS5U',NULL,'7961901823',NULL,NULL,'Pune',NULL,NULL,'341972437443',0.00,5928.00,1,'2026-07-31 21:14:46','2026-07-31 21:14:46',0,NULL,NULL),(100,'Cust_jxs2D0',NULL,'8409657552',NULL,NULL,'Mumbai',NULL,NULL,'396684892076',0.00,1397.00,1,'2026-07-31 21:14:47',NULL,0,NULL,NULL),(101,'Cust_3wDE3n',NULL,'1342036337',NULL,NULL,'Mumbai',NULL,NULL,'540699215575',0.00,4778.00,1,'2026-07-31 21:14:47',NULL,0,NULL,NULL),(102,'Cust_rUFUJk',NULL,'1187911715',NULL,NULL,'Mumbai',NULL,NULL,'621774304192',0.00,552.00,1,'2026-07-31 21:14:47',NULL,0,NULL,NULL),(104,'Cust_LafiMt',NULL,'7374771695',NULL,NULL,'Mumbai',NULL,NULL,'739383183611',0.00,-651313.58,1,'2026-07-31 21:24:28','2026-07-31 21:31:15',0,NULL,NULL),(105,'Cust_wz6vjc',NULL,'7739349163',NULL,NULL,'Pune',NULL,NULL,'143707815447',0.00,-11232.86,1,'2026-07-31 21:24:28','2026-08-01 12:29:21',0,NULL,NULL),(106,'Cust_VG86k8',NULL,'1130953709',NULL,NULL,'Mumbai',NULL,NULL,'805774192773',0.00,7241.00,1,'2026-07-31 21:24:29',NULL,0,NULL,NULL),(107,'Cust_R5C8tm',NULL,'4726078069',NULL,NULL,'Mumbai',NULL,NULL,'800983294756',0.00,5133.00,1,'2026-07-31 21:24:29',NULL,0,NULL,NULL),(116,'yash ','','1234567891',NULL,'',NULL,NULL,NULL,NULL,0.00,102047.49,1,'2026-08-01 23:08:30','2026-08-02 14:26:48',0,NULL,NULL),(118,'hi','','1122334455',NULL,'',NULL,NULL,NULL,NULL,0.00,-11392193.22,1,'2026-08-01 23:49:47','2026-08-02 08:46:48',0,0.000,0.000),(119,'heelo','','1112222355',NULL,'',NULL,NULL,NULL,NULL,0.00,6641.00,1,'2026-08-01 23:56:28','2026-08-02 13:16:02',0,NULL,NULL),(120,'myname','','1234567898',NULL,'',NULL,NULL,NULL,NULL,0.00,85893.00,1,'2026-08-02 08:56:37','2026-08-02 13:15:30',0,0.000,0.000);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `designs`
--

DROP TABLE IF EXISTS `designs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `designs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `design_code` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_designs_design_code` (`design_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `designs`
--

LOCK TABLES `designs` WRITE;
/*!40000 ALTER TABLE `designs` DISABLE KEYS */;
/*!40000 ALTER TABLE `designs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exchange_items`
--

DROP TABLE IF EXISTS `exchange_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exchange_id` int NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `metal` varchar(50) NOT NULL,
  `purity` varchar(50) NOT NULL,
  `touch` decimal(5,2) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `rate_applied` decimal(10,2) NOT NULL,
  `calculated_value` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exchange_id` (`exchange_id`),
  CONSTRAINT `exchange_items_ibfk_1` FOREIGN KEY (`exchange_id`) REFERENCES `exchanges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_items`
--

LOCK TABLES `exchange_items` WRITE;
/*!40000 ALTER TABLE `exchange_items` DISABLE KEYS */;
INSERT INTO `exchange_items` VALUES (1,1,'vvj','Gold','22K',91.60,100.000,1.000,99.000,7245.00,657005.58),(2,2,'gj','Gold','22K',91.60,23.000,2.000,21.000,724.00,13926.86),(3,4,'chao','Gold','22K',91.60,100.000,1.000,99.000,724.00,65655.22),(4,5,'c','Silver','22K',91.60,10.000,0.000,10.000,7245.00,66364.20),(5,6,'442','Gold','22K',91.60,110.000,0.000,110.000,7245.00,730006.20),(6,7,'chain','Gold','22K',91.60,45.000,0.000,45.000,725.00,29884.50),(7,8,'chain','Silver','22K',91.60,12.000,0.000,12.000,724.00,7958.21),(8,9,'chj','Gold','22K',91.60,10.000,0.000,10.000,61.00,558.76),(9,10,'chaiin','Silver','22K',91.60,55.000,0.000,55.000,72.00,3627.36);
/*!40000 ALTER TABLE `exchange_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exchange_new_items`
--

DROP TABLE IF EXISTS `exchange_new_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_new_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exchange_id` int NOT NULL,
  `stock_item_id` int NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `metal` varchar(50) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `final_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exchange_id` (`exchange_id`),
  KEY `stock_item_id` (`stock_item_id`),
  CONSTRAINT `exchange_new_items_ibfk_1` FOREIGN KEY (`exchange_id`) REFERENCES `exchanges` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exchange_new_items_ibfk_2` FOREIGN KEY (`stock_item_id`) REFERENCES `stock_items` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_new_items`
--

LOCK TABLES `exchange_new_items` WRITE;
/*!40000 ALTER TABLE `exchange_new_items` DISABLE KEYS */;
INSERT INTO `exchange_new_items` VALUES (1,3,1,'chain','Gold',100.000,724500.00),(2,4,2,'ring','Gold',1000.000,7245000.00),(3,7,5,'chain','Gold',900.000,202500.00),(4,8,3,'necklace','Silver',110.000,9350.00),(5,9,6,'necklace2 ','Silver',122.000,10470.00),(6,10,7,'chains','Silver',55.000,4675.00);
/*!40000 ALTER TABLE `exchange_new_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exchanges`
--

DROP TABLE IF EXISTS `exchanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchanges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `exchange_date` datetime NOT NULL DEFAULT (now()),
  `total_old_value` decimal(12,2) NOT NULL,
  `total_new_value` decimal(12,2) NOT NULL,
  `gst_amount` decimal(12,2) NOT NULL,
  `grand_total` decimal(12,2) NOT NULL,
  `difference_amount` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_exchanges_customer_id` (`customer_id`),
  CONSTRAINT `exchanges_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchanges`
--

LOCK TABLES `exchanges` WRITE;
/*!40000 ALTER TABLE `exchanges` DISABLE KEYS */;
INSERT INTO `exchanges` VALUES (1,104,'2026-07-31 21:31:15',657005.58,0.00,0.00,0.00,-657005.58),(2,105,'2026-08-01 12:29:21',13926.86,0.00,0.00,0.00,-13926.86),(3,116,'2026-08-02 00:05:30',0.00,724500.00,21735.00,746235.00,746235.00),(4,118,'2026-08-02 01:05:54',65655.22,7245000.00,217350.00,7462350.00,7396694.78),(5,116,'2026-08-02 01:16:00',66364.20,0.00,0.00,0.00,-66364.20),(6,116,'2026-08-02 01:18:50',730006.20,0.00,0.00,0.00,-730006.20),(7,120,'2026-08-02 09:57:25',29884.50,202500.00,6075.00,208575.00,178690.50),(8,116,'2026-08-02 11:25:11',7958.21,9350.00,280.50,9630.50,1672.29),(9,116,'2026-08-02 12:51:15',558.76,10470.00,314.10,10784.10,10225.34),(10,116,'2026-08-02 12:59:38',3627.36,4675.00,140.25,4815.25,1187.89);
/*!40000 ALTER TABLE `exchanges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` enum('SALARY','RENT','ELECTRICITY','MISC') NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `expense_date` date NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_expenses_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `generated_reports`
--

DROP TABLE IF EXISTS `generated_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generated_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `report_name` varchar(255) NOT NULL,
  `report_type` varchar(100) NOT NULL,
  `generated_by` int NOT NULL,
  `generated_at` datetime NOT NULL DEFAULT (now()),
  `s3_file_url` text,
  PRIMARY KEY (`id`),
  KEY `generated_by` (`generated_by`),
  KEY `ix_generated_reports_report_type` (`report_type`),
  KEY `ix_generated_reports_generated_at` (`generated_at`),
  CONSTRAINT `generated_reports_ibfk_1` FOREIGN KEY (`generated_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `generated_reports`
--

LOCK TABLES `generated_reports` WRITE;
/*!40000 ALTER TABLE `generated_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `generated_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gold_calculations`
--

DROP TABLE IF EXISTS `gold_calculations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gold_calculations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_item_id` int NOT NULL,
  `metal_rate_id` int DEFAULT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `making_charges_amount` decimal(10,2) NOT NULL,
  `hallmark_charges` decimal(10,2) NOT NULL,
  `total_gold_value` decimal(12,2) NOT NULL,
  `applied_rate` decimal(10,2) NOT NULL DEFAULT '0.00',
  `making_charge_type` varchar(20) NOT NULL DEFAULT 'flat',
  `making_charge_rate` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_item_id` (`invoice_item_id`),
  KEY `ix_gold_calculations_metal_rate_id` (`metal_rate_id`),
  CONSTRAINT `gold_calculations_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `gold_calculations_ibfk_2` FOREIGN KEY (`metal_rate_id`) REFERENCES `gold_rates` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gold_calculations`
--

LOCK TABLES `gold_calculations` WRITE;
/*!40000 ALTER TABLE `gold_calculations` DISABLE KEYS */;
INSERT INTO `gold_calculations` VALUES (1,6,NULL,100.000,0.000,100.000,0.00,0.00,724500.00,7245.00,'flat',0.00),(2,7,NULL,100.000,0.000,100.000,0.00,0.00,724500.00,7245.00,'flat',0.00),(3,9,NULL,3.000,0.000,3.000,1950.00,120.00,21735.00,7245.00,'flat',0.00),(4,12,NULL,100.000,0.000,100.000,0.00,0.00,724500.00,7245.00,'flat',0.00),(5,14,NULL,15.000,0.000,15.000,9750.00,120.00,118650.00,7910.00,'flat',0.00),(6,16,NULL,100.000,0.000,100.000,0.00,0.00,724500.00,7245.00,'flat',0.00),(7,20,NULL,80.000,2.000,78.000,50700.00,120.00,565500.00,7250.00,'flat',0.00),(8,22,NULL,100.000,0.000,100.000,65000.00,120.00,725000.00,7250.00,'flat',0.00),(9,46,NULL,10.000,1.000,9.000,41.00,0.00,65205.00,7245.00,'flat',0.00),(10,48,NULL,10.000,1.000,9.000,41.00,0.00,65205.00,7245.00,'flat',0.00);
/*!40000 ALTER TABLE `gold_calculations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gold_purchases`
--

DROP TABLE IF EXISTS `gold_purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gold_purchases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `invoice_number` varchar(50) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) DEFAULT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `touch` decimal(5,2) NOT NULL,
  `purity` varchar(20) DEFAULT NULL,
  `todays_rate` decimal(12,2) NOT NULL,
  `purchase_rate` decimal(12,2) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `gst_amount` decimal(12,2) DEFAULT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `purchase_date` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `supplier_id` (`supplier_id`),
  KEY `ix_gold_purchases_id` (`id`),
  CONSTRAINT `gold_purchases_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gold_purchases`
--

LOCK TABLES `gold_purchases` WRITE;
/*!40000 ALTER TABLE `gold_purchases` DISABLE KEYS */;
/*!40000 ALTER TABLE `gold_purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gold_rates`
--

DROP TABLE IF EXISTS `gold_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gold_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purity_id` int NOT NULL,
  `rate_per_gram` decimal(12,2) NOT NULL,
  `effective_datetime` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `purity_id` (`purity_id`),
  KEY `ix_gold_rates_effective_datetime` (`effective_datetime`),
  CONSTRAINT `gold_rates_ibfk_1` FOREIGN KEY (`purity_id`) REFERENCES `purities` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gold_rates`
--

LOCK TABLES `gold_rates` WRITE;
/*!40000 ALTER TABLE `gold_rates` DISABLE KEYS */;
/*!40000 ALTER TABLE `gold_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(100) NOT NULL,
  `category_id` int DEFAULT NULL,
  `metal_type` enum('GOLD','SILVER') NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `purity` varchar(20) DEFAULT NULL,
  `design_code` varchar(50) DEFAULT NULL,
  `status` enum('AVAILABLE','SOLD','RESERVED') DEFAULT NULL,
  `qr_code_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `touch` decimal(5,2) DEFAULT NULL,
  `item_code` varchar(20) DEFAULT NULL,
  `qr_image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `qr_code_id` (`qr_code_id`),
  KEY `category_id` (`category_id`),
  KEY `ix_inventory_id` (`id`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`qr_code_id`) REFERENCES `qr_inventory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_items`
--

DROP TABLE IF EXISTS `inventory_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_variant_id` int NOT NULL,
  `warehouse_id` int NOT NULL,
  `barcode` varchar(100) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `status` enum('AVAILABLE','SOLD','RESERVED') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_inventory_items_barcode` (`barcode`),
  KEY `ix_inventory_items_status` (`status`),
  KEY `ix_inventory_items_product_variant_id` (`product_variant_id`),
  KEY `ix_inventory_items_warehouse_id` (`warehouse_id`),
  CONSTRAINT `inventory_items_ibfk_1` FOREIGN KEY (`product_variant_id`) REFERENCES `product_variants` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `inventory_items_ibfk_2` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_items`
--

LOCK TABLES `inventory_items` WRITE;
/*!40000 ALTER TABLE `inventory_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_transactions`
--

DROP TABLE IF EXISTS `inventory_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_item_id` int NOT NULL,
  `transaction_type` enum('IN','OUT','TRANSFER','ADJUSTMENT') NOT NULL,
  `quantity` int NOT NULL,
  `date` datetime NOT NULL DEFAULT (now()),
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_item_id` (`inventory_item_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_inventory_transactions_date` (`date`),
  CONSTRAINT `inventory_transactions_ibfk_1` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `inventory_transactions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_transactions`
--

LOCK TABLES `inventory_transactions` WRITE;
/*!40000 ALTER TABLE `inventory_transactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_items`
--

DROP TABLE IF EXISTS `invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `inventory_item_id` int DEFAULT NULL,
  `item_name` varchar(200) DEFAULT NULL,
  `item_type` enum('GOLD','SILVER','DIAMOND') NOT NULL,
  `final_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_invoice_items_invoice_id` (`invoice_id`),
  KEY `ix_invoice_items_inventory_item_id` (`inventory_item_id`),
  CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_items`
--

LOCK TABLES `invoice_items` WRITE;
/*!40000 ALTER TABLE `invoice_items` DISABLE KEYS */;
INSERT INTO `invoice_items` VALUES (4,4,NULL,'chain','SILVER',9000.00),(5,5,NULL,'yash','SILVER',9000.00),(6,6,NULL,'chain','GOLD',724500.00),(7,7,NULL,'chain','GOLD',724500.00),(8,8,NULL,'chaini','SILVER',5070.00),(9,9,NULL,'gilfsi','GOLD',22229.26),(10,10,NULL,'ring','SILVER',49290.00),(11,11,NULL,'ring','SILVER',9000.00),(12,12,NULL,'chain','GOLD',724500.00),(13,13,NULL,'Silver Item','SILVER',2655.00),(14,14,NULL,'Gold Item','GOLD',128401.35),(15,15,NULL,'chain','SILVER',585300.00),(16,16,NULL,'chain','GOLD',724500.00),(17,17,NULL,'Silver Item','SILVER',1791.00),(18,17,NULL,'Silver Item','SILVER',3520.00),(19,18,NULL,'Silver Item','SILVER',885.00),(20,19,NULL,'Gold Item','GOLD',568821.00),(21,19,NULL,'Silver Item','SILVER',1062.00),(22,20,NULL,'Gold Item','GOLD',729220.00),(23,21,NULL,'chain','SILVER',8253.00),(24,22,NULL,'payal','SILVER',24163.20),(25,23,NULL,'necklace','SILVER',9900.00),(26,24,NULL,'necklace','SILVER',9900.00),(27,25,NULL,'necklace','SILVER',9900.00),(28,26,NULL,'necklace','SILVER',9900.00),(29,27,NULL,'necklace','SILVER',9900.00),(30,28,NULL,'necklace','SILVER',9900.00),(31,29,NULL,'necklace','SILVER',9900.00),(32,30,NULL,'necklace','SILVER',9900.00),(33,31,NULL,'necklace','SILVER',9900.00),(34,32,NULL,'necklace','SILVER',9900.00),(35,33,NULL,'necklace','SILVER',9900.00),(36,34,NULL,'necklace','SILVER',9900.00),(37,35,NULL,'necklace','SILVER',9900.00),(38,36,NULL,'necklace','SILVER',9900.00),(39,37,NULL,'necklace','SILVER',9900.00),(40,38,NULL,'necklace','SILVER',9900.00),(41,39,NULL,'necklace','SILVER',9900.00),(42,39,NULL,'necklace2 ','SILVER',11080.00),(43,40,NULL,'necklace2 ','SILVER',11080.00),(44,41,NULL,'rr','SILVER',223440.00),(45,42,NULL,'ffs','SILVER',27060.00),(46,43,NULL,'coin','GOLD',65246.00),(47,44,NULL,'coin','SILVER',6523.00),(48,45,NULL,'coin','GOLD',65246.00),(49,46,NULL,'coin','SILVER',6523.00),(50,47,NULL,'ring','SILVER',6840.00);
/*!40000 ALTER TABLE `invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int DEFAULT NULL,
  `invoice_number` varchar(100) NOT NULL,
  `invoice_date` datetime NOT NULL DEFAULT (now()),
  `subtotal` decimal(12,2) NOT NULL,
  `tax_amount` decimal(12,2) NOT NULL,
  `discount_amount` decimal(12,2) NOT NULL,
  `grand_total` decimal(12,2) NOT NULL,
  `status` enum('Draft','Partial','Paid','Completed','Cancelled') DEFAULT 'Draft',
  `created_by` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_invoices_invoice_number` (`invoice_number`),
  KEY `created_by` (`created_by`),
  KEY `ix_invoices_status` (`status`),
  KEY `ix_invoices_invoice_date` (`invoice_date`),
  KEY `invoices_ibfk_1` (`customer_id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (4,NULL,'INV-20260801-0001','2026-08-01 12:47:44',9000.00,270.00,0.00,9270.00,'Paid',197),(5,87,'INV-20260801-0002','2026-08-01 12:48:38',9000.00,270.00,0.00,9270.00,'Paid',197),(6,NULL,'INV-20260801-0003','2026-08-01 22:33:02',724500.00,21735.00,0.00,746235.00,'Paid',197),(7,NULL,'INV-20260801-0004','2026-08-01 22:39:10',724500.00,21735.00,0.00,746235.00,'Paid',197),(8,NULL,'INV-20260801-0005','2026-08-01 22:46:29',5070.00,152.10,0.00,5222.00,'Paid',197),(9,NULL,'INV-20260801-0006','2026-08-01 22:52:46',22229.26,666.88,0.00,22896.00,'Paid',197),(10,116,'INV-20260801-0007','2026-08-01 23:08:06',49290.00,1478.70,0.00,50769.00,'Paid',197),(11,NULL,'INV-20260801-0008','2026-08-01 23:16:44',9000.00,270.00,0.00,9270.00,'Paid',197),(12,62,'INV-20260801-0009','2026-08-01 23:22:53',724500.00,21735.00,0.00,746235.00,'Paid',197),(13,88,'INV-20260801-0010','2026-08-01 23:47:01',2655.00,79.65,0.00,2735.00,'Paid',197),(14,118,'INV-20260801-0011','2026-08-01 23:49:31',128401.35,3852.04,0.00,132253.00,'Paid',197),(15,119,'INV-20260801-0012','2026-08-01 23:56:05',585300.00,17559.00,0.00,602859.00,'Cancelled',197),(16,NULL,'INV-20260802-0001','2026-08-02 00:00:20',724500.00,21735.00,0.00,746235.00,'Paid',197),(17,NULL,'INV-20260802-0002','2026-08-02 00:13:20',5311.00,159.33,0.00,5470.00,'Paid',197),(18,86,'INV-20260802-0003','2026-08-02 00:17:03',885.00,26.55,0.00,912.00,'Paid',197),(19,86,'INV-20260802-0004','2026-08-02 00:20:10',569883.00,17096.49,0.00,586979.00,'Paid',197),(20,63,'INV-20260802-0005','2026-08-02 01:46:10',729220.00,21876.60,0.00,751097.00,'Paid',197),(21,116,'INV-20260802-0006','2026-08-02 08:34:57',8253.00,247.59,0.00,8501.00,'Paid',197),(22,120,'INV-20260802-0007','2026-08-02 08:56:18',24163.20,724.90,0.00,24888.00,'Paid',197),(23,NULL,'INV-20260802-0008','2026-08-02 11:13:17',9900.00,297.00,0.00,10197.00,'Paid',197),(24,116,'INV-20260802-0009','2026-08-02 11:15:34',9900.00,297.00,0.00,10197.00,'Draft',197),(25,116,'INV-20260802-0010','2026-08-02 11:20:13',9900.00,297.00,0.00,10197.00,'Partial',197),(26,116,'INV-20260802-0011','2026-08-02 11:20:16',9900.00,297.00,0.00,10197.00,'Partial',197),(27,116,'INV-20260802-0012','2026-08-02 11:20:16',9900.00,297.00,0.00,10197.00,'Partial',197),(28,116,'INV-20260802-0013','2026-08-02 11:20:18',9900.00,297.00,0.00,10197.00,'Partial',197),(29,116,'INV-20260802-0014','2026-08-02 11:20:18',9900.00,297.00,0.00,10197.00,'Partial',197),(30,116,'INV-20260802-0015','2026-08-02 11:20:19',9900.00,297.00,0.00,10197.00,'Partial',197),(31,116,'INV-20260802-0016','2026-08-02 11:20:19',9900.00,297.00,0.00,10197.00,'Partial',197),(32,116,'INV-20260802-0017','2026-08-02 11:20:19',9900.00,297.00,0.00,10197.00,'Partial',197),(33,116,'INV-20260802-0018','2026-08-02 11:20:48',9900.00,297.00,0.00,10197.00,'Partial',197),(34,116,'INV-20260802-0019','2026-08-02 11:23:00',9900.00,297.00,0.00,10197.00,'Partial',197),(35,116,'INV-20260802-0020','2026-08-02 11:23:02',9900.00,297.00,0.00,10197.00,'Partial',197),(36,116,'INV-20260802-0021','2026-08-02 11:23:05',9900.00,297.00,0.00,10197.00,'Partial',197),(37,116,'INV-20260802-0022','2026-08-02 11:23:05',9900.00,297.00,0.00,10197.00,'Partial',197),(38,116,'INV-20260802-0023','2026-08-02 11:23:05',9900.00,297.00,0.00,10197.00,'Partial',197),(39,116,'INV-20260802-0024','2026-08-02 11:31:21',20980.00,629.40,0.00,21609.00,'Partial',197),(40,89,'INV-20260802-0025','2026-08-02 11:32:26',11080.00,332.40,0.00,11412.00,'Partial',197),(41,116,'INV-20260802-0026','2026-08-02 12:56:37',223440.00,6703.20,0.00,230143.00,'Completed',197),(42,116,'INV-20260802-0027','2026-08-02 12:57:25',27060.00,0.00,0.00,27060.00,'Completed',197),(43,120,'INV-20260802-0028','2026-08-02 13:15:30',65246.00,1957.38,0.00,67203.00,'Completed',197),(44,119,'INV-20260802-0029','2026-08-02 13:16:02',6523.00,195.69,0.00,6719.00,'Completed',197),(45,116,'INV-20260802-0030','2026-08-02 13:19:21',65246.00,0.00,0.00,65246.00,'Completed',197),(46,116,'INV-20260802-0031','2026-08-02 13:59:11',6523.00,195.69,0.00,6719.00,'Completed',197),(47,116,'INV-20260802-0032','2026-08-02 14:26:48',6840.00,205.20,0.00,7045.00,'Completed',197);
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metal_rates`
--

DROP TABLE IF EXISTS `metal_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metal_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `metal_type` varchar(20) NOT NULL,
  `rate_per_gram` decimal(12,2) NOT NULL,
  `purity` varchar(20) DEFAULT NULL,
  `date` date NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`),
  KEY `ix_metal_rates_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metal_rates`
--

LOCK TABLES `metal_rates` WRITE;
/*!40000 ALTER TABLE `metal_rates` DISABLE KEYS */;
/*!40000 ALTER TABLE `metal_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metal_types`
--

DROP TABLE IF EXISTS `metal_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metal_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metal_types`
--

LOCK TABLES `metal_types` WRITE;
/*!40000 ALTER TABLE `metal_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `metal_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_id` int DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `supplier_id` int DEFAULT NULL,
  `amount` decimal(12,2) NOT NULL,
  `payment_mode` enum('CASH','UPI','BANK','CARD') NOT NULL,
  `reference_number` varchar(100) DEFAULT NULL,
  `payment_date` datetime DEFAULT (now()),
  `notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  KEY `customer_id` (`customer_id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `ix_payments_id` (`id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `bills` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_permissions_name` (`name`),
  KEY `ix_permissions_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `image_url` varchar(500) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_variant_stones`
--

DROP TABLE IF EXISTS `product_variant_stones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_variant_stones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `variant_id` int NOT NULL,
  `stone_id` int NOT NULL,
  `weight_carat` decimal(10,3) NOT NULL,
  `pieces` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `variant_id` (`variant_id`),
  KEY `stone_id` (`stone_id`),
  CONSTRAINT `product_variant_stones_ibfk_1` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_variant_stones_ibfk_2` FOREIGN KEY (`stone_id`) REFERENCES `stones` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_variant_stones`
--

LOCK TABLES `product_variant_stones` WRITE;
/*!40000 ALTER TABLE `product_variant_stones` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_variant_stones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_variants`
--

DROP TABLE IF EXISTS `product_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_variants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `purity_id` int NOT NULL,
  `standard_weight` decimal(10,3) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `making_charge_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_product_variants_product_id` (`product_id`),
  KEY `ix_product_variants_purity_id` (`purity_id`),
  CONSTRAINT `product_variants_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_variants_ibfk_2` FOREIGN KEY (`purity_id`) REFERENCES `purities` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_variants`
--

LOCK TABLES `product_variants` WRITE;
/*!40000 ALTER TABLE `product_variants` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_variants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int DEFAULT NULL,
  `design_id` int DEFAULT NULL,
  `metal_type_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `sku_prefix` varchar(50) NOT NULL,
  `description` text,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_products_sku_prefix` (`sku_prefix`),
  KEY `category_id` (`category_id`),
  KEY `design_id` (`design_id`),
  KEY `metal_type_id` (`metal_type_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`design_id`) REFERENCES `designs` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_ibfk_3` FOREIGN KEY (`metal_type_id`) REFERENCES `metal_types` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_items`
--

DROP TABLE IF EXISTS `purchase_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_id` int NOT NULL,
  `metal_type` varchar(50) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `touch_purity` decimal(5,2) NOT NULL,
  `wastage` decimal(5,2) NOT NULL,
  `fine_weight` decimal(10,3) NOT NULL,
  `metal_rate` decimal(10,2) NOT NULL,
  `metal_value` decimal(12,2) NOT NULL,
  `labour_charge` decimal(10,2) NOT NULL,
  `testing_melting_charge` decimal(10,2) NOT NULL,
  `hallmark_charge` decimal(10,2) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  `taxable_amount` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_id` (`purchase_id`),
  CONSTRAINT `purchase_items_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `purchases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_items`
--

LOCK TABLES `purchase_items` WRITE;
/*!40000 ALTER TABLE `purchase_items` DISABLE KEYS */;
INSERT INTO `purchase_items` VALUES (1,14,'Silver','gols','Scrap',25.000,0.000,25.000,7.00,42.00,1.750,24.00,42.00,0.00,0.00,0.00,0.00,0.00,42.00),(2,15,'Silver','chian','Scrap',1000.000,0.000,1000.000,74.00,14.00,740.000,123.00,91020.00,0.00,0.00,0.00,0.00,0.00,91020.00),(3,16,'Silver','chain','Scrap',100.000,0.000,100.000,88.00,1.00,88.000,18.00,1584.00,0.00,0.00,0.00,0.00,0.00,1584.00),(4,17,'Gold','chain','dsf',10.000,0.000,10.000,78.00,0.00,7.800,100.00,780.00,0.00,0.00,0.00,0.00,0.00,780.00),(5,17,'Silver','chian','Scrap',10.000,0.000,10.000,8.00,74.00,0.800,148.00,118.40,0.00,0.00,0.00,0.00,0.00,118.40),(6,18,'Gold','2210','Scrap',252.000,1.000,251.000,99.60,0.00,249.996,12.00,2999.95,0.00,0.00,0.00,0.00,0.00,2999.95),(7,19,'Gold','payal','chain',102.000,0.000,102.000,78.00,0.00,79.560,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(8,20,'Gold','chain','gold',15.000,0.000,15.000,78.00,0.00,11.700,71.00,830.70,0.00,0.00,0.00,0.00,0.00,830.70),(9,21,'Silver','coin','Scrap',56.000,0.000,56.000,78.00,5.00,43.680,101.00,4411.68,0.00,0.00,0.00,0.00,0.00,4411.68),(10,21,'Gold','coi','Scrap',20.000,0.000,20.000,45.00,0.00,9.000,788.00,7092.00,0.00,0.00,0.00,0.00,0.00,7092.00),(11,22,'Gold','ring','iids',155.000,0.000,155.000,55.00,0.00,85.250,12.00,1023.00,0.00,0.00,0.00,0.00,0.00,1023.00),(12,23,'Gold','yyy','ghg',12.000,0.000,12.000,87.00,0.00,10.440,458.00,4781.52,0.00,0.00,0.00,0.00,0.00,4781.52),(13,24,'Silver','ff','Scrap',78.000,0.000,78.000,0.00,48.00,0.000,88.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(14,25,'Silver','dyfs','Scrap',778.000,0.000,778.000,0.00,78.00,0.000,61.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(15,26,'Silver','coin','Scrap',87.000,0.000,87.000,0.00,82.00,0.000,85.00,0.00,0.00,78.00,0.00,58.00,78.00,58.00),(16,27,'Silver','coin','Scrap',78.000,0.000,78.000,0.00,78.00,0.000,785.00,0.00,0.00,78.00,0.00,100.00,78.00,100.00),(17,32,'Silver','coin','Scrap',45.000,0.000,45.000,0.00,78.00,35.100,100.00,3510.00,0.00,0.00,0.00,0.00,0.00,3510.00);
/*!40000 ALTER TABLE `purchase_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_number` varchar(50) NOT NULL,
  `seller_id` int NOT NULL,
  `created_by_id` int NOT NULL,
  `created_at` datetime NOT NULL,
  `total_taxable` decimal(12,2) NOT NULL,
  `cgst` decimal(10,2) NOT NULL,
  `sgst` decimal(10,2) NOT NULL,
  `igst` decimal(10,2) NOT NULL,
  `grand_total` decimal(12,2) NOT NULL,
  `status` enum('COMPLETED','DRAFT','CANCELLED') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_purchases_purchase_number` (`purchase_number`),
  KEY `seller_id` (`seller_id`),
  KEY `created_by_id` (`created_by_id`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`id`),
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (14,'PUR-930759',26,197,'2026-08-01 17:05:31',42.00,0.63,0.63,0.00,43.26,'COMPLETED'),(15,'PUR-66050',27,197,'2026-08-01 17:07:46',91020.00,1365.30,1365.30,0.00,93750.60,'COMPLETED'),(16,'PUR-516806',28,197,'2026-08-01 17:15:17',1584.00,23.76,23.76,0.00,1631.52,'COMPLETED'),(17,'PUR-409547',29,197,'2026-08-01 18:53:30',898.40,13.48,13.48,0.00,925.36,'COMPLETED'),(18,'PUR-849236',30,197,'2026-08-01 19:50:49',2999.95,45.00,45.00,0.00,3089.95,'COMPLETED'),(19,'PUR-720178',31,197,'2026-08-02 03:52:00',0.00,0.00,0.00,0.00,0.00,'COMPLETED'),(20,'PUR-287061',31,197,'2026-08-02 04:01:27',830.70,12.46,12.46,0.00,855.62,'COMPLETED'),(21,'PUR-347788',31,197,'2026-08-02 04:19:08',11503.68,172.56,172.56,0.00,11848.80,'COMPLETED'),(22,'PUR-302936',30,197,'2026-08-02 05:58:23',1023.00,15.35,15.35,0.00,1053.70,'COMPLETED'),(23,'PUR-15289',13,197,'2026-08-02 06:10:15',4781.52,71.72,71.72,0.00,4924.96,'COMPLETED'),(24,'PUR-458483',28,197,'2026-08-02 07:24:18',0.00,0.00,0.00,0.00,0.00,'COMPLETED'),(25,'PUR-975630',28,197,'2026-08-02 07:32:56',0.00,0.00,0.00,0.00,0.00,'COMPLETED'),(26,'PUR-259627',26,197,'2026-08-02 07:54:20',58.00,0.87,0.87,0.00,59.74,'COMPLETED'),(27,'PUR-346857',28,197,'2026-08-02 07:55:47',100.00,1.50,1.50,0.00,103.00,'COMPLETED'),(32,'PUR-505286',28,197,'2026-08-02 08:15:05',3510.00,52.65,52.65,0.00,3615.30,'COMPLETED');
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purities`
--

DROP TABLE IF EXISTS `purities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `metal_type_id` int NOT NULL,
  `karat_name` varchar(50) NOT NULL,
  `percentage` decimal(5,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_purities_metal_type_id` (`metal_type_id`),
  CONSTRAINT `purities_ibfk_1` FOREIGN KEY (`metal_type_id`) REFERENCES `metal_types` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purities`
--

LOCK TABLES `purities` WRITE;
/*!40000 ALTER TABLE `purities` DISABLE KEYS */;
/*!40000 ALTER TABLE `purities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qr_inventory`
--

DROP TABLE IF EXISTS `qr_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qr_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_code` varchar(20) NOT NULL,
  `qr_image_path` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_qr_inventory_item_code` (`item_code`),
  KEY `ix_qr_inventory_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qr_inventory`
--

LOCK TABLES `qr_inventory` WRITE;
/*!40000 ALTER TABLE `qr_inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `qr_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_roles_name` (`name`),
  KEY `ix_roles_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=233 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (155,'Admin','Super Administrator');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sellers`
--

DROP TABLE IF EXISTS `sellers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sellers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `aadhaar_pan` varchar(50) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `gst_number` varchar(20) DEFAULT NULL,
  `outstanding_balance` decimal(12,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `fine_gold_balance` decimal(10,3) NOT NULL,
  `fine_silver_balance` decimal(10,3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_sellers_name` (`name`),
  KEY `ix_sellers_mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sellers`
--

LOCK TABLES `sellers` WRITE;
/*!40000 ALTER TABLE `sellers` DISABLE KEYS */;
INSERT INTO `sellers` VALUES (1,'Supp_9HmB5d','4515059077',NULL,NULL,'Surat','24ABCDE7422F1Z5',38146.00,1,0.000,0.000),(2,'Supp_Kax2xx','8833323286',NULL,NULL,'Ahmedabad','24ABCDE1464F1Z5',2815.00,1,0.000,0.000),(3,'Supp_4tHKyp','8112078533',NULL,NULL,'Ahmedabad','24ABCDE4715F1Z5',8810.00,1,0.000,0.000),(4,'Supp_WxpmJt','5230112154',NULL,NULL,'Surat','24ABCDE7100F1Z5',46550.00,1,0.000,0.000),(5,'Supp_Kfe0rS','7722686912',NULL,NULL,'Ahmedabad','24ABCDE9565F1Z5',40326.00,1,0.000,0.000),(6,'Supp_W7v1bH','6072503168',NULL,NULL,'Surat','24ABCDE4566F1Z5',37616.00,1,0.000,0.000),(8,'Supp_ooubYc','1200579551',NULL,NULL,'Surat','24ABCDE2878F1Z5',47133.00,1,0.000,0.000),(9,'Supp_dAgrRT','4367837197',NULL,NULL,'Ahmedabad','24ABCDE9870F1Z5',162.00,1,0.000,0.000),(10,'Supp_Rab9xT','1469504622',NULL,NULL,'Surat','24ABCDE5589F1Z5',23954.00,1,0.000,0.000),(11,'Supp_dbVCqE','1798719095',NULL,NULL,'Ahmedabad','24ABCDE2395F1Z5',45764.00,1,0.000,0.000),(12,'Supp_5tgLCw','9249746677',NULL,NULL,'Surat','24ABCDE5632F1Z5',41592.00,1,0.000,0.000),(13,'Supp_VrEBx6','9265322365',NULL,NULL,'Ahmedabad','24ABCDE6756F1Z5',23828.99,1,0.000,0.000),(26,'yash','2402042',NULL,'',NULL,'',-6085.14,1,0.000,0.000),(27,'sony','34553531',NULL,'',NULL,'',0.00,1,0.000,0.000),(28,'vansh','02725',NULL,'',NULL,'',-6668.16,1,0.000,0.000),(29,'yad','1110402',NULL,'',NULL,'',925.36,1,0.000,0.000),(30,'yy','11111111',NULL,'',NULL,'',3643.65,1,0.000,0.000),(31,'me','1234567894',NULL,'',NULL,'',2403.73,1,0.000,0.000),(32,'ys','45678945612',NULL,NULL,'','',0.00,1,0.000,0.000);
/*!40000 ALTER TABLE `sellers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(50) NOT NULL,
  `value` text NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_settings_key` (`key`),
  KEY `ix_settings_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'test','test','Test setting',NULL),(2,'test2','test2',NULL,NULL),(3,'business_name','Saideep',NULL,NULL),(4,'gstin','bbfs553e',NULL,NULL),(5,'address','Talkhatgarh',NULL,NULL);
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `silver_calculations`
--

DROP TABLE IF EXISTS `silver_calculations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `silver_calculations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_item_id` int NOT NULL,
  `metal_rate_id` int DEFAULT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `tanch_percentage` decimal(5,2) NOT NULL,
  `pure_weight` decimal(10,3) NOT NULL,
  `making_charges_amount` decimal(10,2) NOT NULL,
  `total_silver_value` decimal(12,2) NOT NULL,
  `applied_rate` decimal(10,2) NOT NULL DEFAULT '0.00',
  `making_charge_type` varchar(20) NOT NULL DEFAULT 'flat',
  `making_charge_rate` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_item_id` (`invoice_item_id`),
  KEY `ix_silver_calculations_metal_rate_id` (`metal_rate_id`),
  CONSTRAINT `silver_calculations_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `silver_calculations_ibfk_2` FOREIGN KEY (`metal_rate_id`) REFERENCES `silver_rates` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `silver_calculations`
--

LOCK TABLES `silver_calculations` WRITE;
/*!40000 ALTER TABLE `silver_calculations` DISABLE KEYS */;
INSERT INTO `silver_calculations` VALUES (1,4,NULL,100.000,65.00,65.000,3000.00,5850.00,90.00,'flat',0.00),(2,5,NULL,100.000,65.00,65.000,3000.00,5850.00,90.00,'flat',0.00),(3,8,NULL,8.000,65.00,5.200,240.00,4680.00,900.00,'flat',0.00),(4,10,NULL,455.000,65.00,295.750,13650.00,35490.00,120.00,'flat',0.00),(5,11,NULL,100.000,65.00,65.000,3000.00,5850.00,90.00,'flat',0.00),(6,13,NULL,30.000,65.00,19.500,900.00,1755.00,90.00,'flat',0.00),(7,15,NULL,10.000,65.00,6.500,300.00,585000.00,90000.00,'flat',0.00),(8,17,NULL,20.000,65.00,13.000,620.00,1170.00,90.00,'flat',0.00),(9,18,NULL,100.000,65.00,65.000,3000.00,520.00,8.00,'flat',0.00),(10,19,NULL,10.000,65.00,6.500,300.00,585.00,90.00,'flat',0.00),(11,21,NULL,12.000,65.00,7.800,360.00,702.00,90.00,'flat',0.00),(12,23,NULL,131.000,70.00,91.700,0.00,8253.00,90.00,'flat',0.00),(13,24,NULL,144.000,65.00,93.600,4320.00,19843.20,212.00,'flat',0.00),(14,25,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(15,26,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(16,27,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(17,28,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(18,29,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(19,30,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(20,31,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(21,32,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(22,33,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(23,34,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(24,35,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(25,36,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(26,37,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(27,38,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(28,39,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(29,40,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(30,41,NULL,110.000,100.00,110.000,0.00,9900000.00,90000.00,'flat',0.00),(31,42,NULL,122.000,100.00,122.000,100.00,10980000.00,90000.00,'flat',0.00),(32,43,NULL,122.000,100.00,122.000,100.00,10980000.00,90000.00,'flat',0.00),(33,44,NULL,38.000,65.00,24.700,1140.00,222300.00,9000.00,'flat',0.00),(34,45,NULL,44.000,65.00,28.600,1320.00,25740.00,900.00,'flat',0.00),(35,47,NULL,78.000,89.74,70.000,78.00,6300000.00,90000.00,'flat',0.00),(36,49,NULL,78.000,89.74,70.000,78.00,6300000.00,90000.00,'flat',0.00),(37,50,NULL,78.000,97.44,76.000,0.00,6840000.00,90000.00,'flat',0.00);
/*!40000 ALTER TABLE `silver_calculations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `silver_purchases`
--

DROP TABLE IF EXISTS `silver_purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `silver_purchases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `invoice_number` varchar(50) NOT NULL,
  `weight` decimal(10,3) NOT NULL,
  `tanch` decimal(5,2) NOT NULL,
  `wastage` decimal(5,2) DEFAULT NULL,
  `final_tanch` decimal(5,2) NOT NULL,
  `recovered_silver` decimal(10,3) NOT NULL,
  `todays_rate` decimal(12,2) NOT NULL,
  `silver_value` decimal(12,2) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `gst_amount` decimal(12,2) DEFAULT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `purchase_date` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `supplier_id` (`supplier_id`),
  KEY `ix_silver_purchases_id` (`id`),
  CONSTRAINT `silver_purchases_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `silver_purchases`
--

LOCK TABLES `silver_purchases` WRITE;
/*!40000 ALTER TABLE `silver_purchases` DISABLE KEYS */;
/*!40000 ALTER TABLE `silver_purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `silver_rates`
--

DROP TABLE IF EXISTS `silver_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `silver_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purity_id` int NOT NULL,
  `rate_per_gram` decimal(12,2) NOT NULL,
  `effective_datetime` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `purity_id` (`purity_id`),
  KEY `ix_silver_rates_effective_datetime` (`effective_datetime`),
  CONSTRAINT `silver_rates_ibfk_1` FOREIGN KEY (`purity_id`) REFERENCES `purities` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `silver_rates`
--

LOCK TABLES `silver_rates` WRITE;
/*!40000 ALTER TABLE `silver_rates` DISABLE KEYS */;
/*!40000 ALTER TABLE `silver_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_items`
--

DROP TABLE IF EXISTS `stock_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_code` varchar(50) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `metal` varchar(50) NOT NULL,
  `category` varchar(100) NOT NULL,
  `hsn` varchar(50) DEFAULT NULL,
  `purity` varchar(50) DEFAULT NULL,
  `tanch` decimal(10,2) DEFAULT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `making_type` varchar(50) DEFAULT NULL,
  `making_charge` decimal(10,2) NOT NULL,
  `hallmark` decimal(10,2) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `shelf` varchar(100) DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `qr_code_path` varchar(255) DEFAULT NULL,
  `description` text,
  `status` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_stock_items_item_code` (`item_code`),
  KEY `ix_stock_items_category` (`category`),
  KEY `ix_stock_items_metal` (`metal`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_items`
--

LOCK TABLES `stock_items` WRITE;
/*!40000 ALTER TABLE `stock_items` DISABLE KEYS */;
INSERT INTO `stock_items` VALUES (1,'GLD-000001','chain','Gold','ring','','22K916',NULL,100.000,0.000,100.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/GLD-000001.png','','Sold','2026-07-31 16:00:17','2026-08-01 18:35:30'),(2,'GLD-000002','ring','Gold','rff','','22K916',NULL,1000.000,0.000,1000.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/GLD-000002.png','','Sold','2026-08-01 19:25:33','2026-08-01 19:35:54'),(3,'SLV-000001','necklace','Silver','necklace','','22K916',NULL,110.000,0.000,110.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000001.png','','Sold','2026-08-01 20:03:26','2026-08-02 05:55:12'),(5,'GLD-000003','chain','Gold','','','22K916',79.00,900.000,0.000,900.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/GLD-000003.png','','Sold','2026-08-01 20:11:34','2026-08-02 04:27:26'),(6,'SLV-000002','necklace2 ','Silver','dd','','9.16',80.00,122.000,0.000,122.000,'flat',100.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000002.png','','Sold','2026-08-02 06:00:55','2026-08-02 07:21:15'),(7,'SLV-000003','chains','Silver','ring','','22K916',69.00,55.000,0.000,55.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000003.png','','Sold','2026-08-02 07:28:54','2026-08-02 07:29:38'),(8,'SLV-000004','coin','Silver','','','22K916',78.00,78.000,8.000,70.000,'flat',78.00,70.00,75.00,'min','1',NULL,'/static/qrcodes/SLV-000004.png','','Sold','2026-08-02 07:44:11','2026-08-02 08:29:11'),(9,'GLD-000004','coin','Gold','sii','','22K916',78.00,10.000,1.000,9.000,'flat',41.00,0.00,0.00,'','7',NULL,'/static/qrcodes/GLD-000004.png','','Sold','2026-08-02 07:44:48','2026-08-02 07:49:22'),(10,'SLV-000005','coin','Silver','fsf','','22K916',78.00,78.000,0.000,78.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000005.png','','Available','2026-08-02 08:51:06','2026-08-02 08:51:06'),(11,'SLV-000006','ring','Silver','ring','','22K916',97.00,78.000,2.000,76.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000006.png','','Sold','2026-08-02 08:54:19','2026-08-02 08:56:48');
/*!40000 ALTER TABLE `stock_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stones`
--

DROP TABLE IF EXISTS `stones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `stone_type` varchar(100) NOT NULL,
  `default_rate_per_carat` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stones`
--

LOCK TABLES `stones` WRITE;
/*!40000 ALTER TABLE `stones` DISABLE KEYS */;
/*!40000 ALTER TABLE `stones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier_ledgers`
--

DROP TABLE IF EXISTS `supplier_ledgers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier_ledgers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `seller_id` int NOT NULL,
  `date` datetime NOT NULL,
  `voucher_type` varchar(50) NOT NULL,
  `voucher_number` varchar(50) DEFAULT NULL,
  `description` text,
  `debit` decimal(12,2) NOT NULL,
  `credit` decimal(12,2) NOT NULL,
  `balance` decimal(12,2) NOT NULL,
  `gold_debit` decimal(10,3) NOT NULL,
  `gold_credit` decimal(10,3) NOT NULL,
  `gold_balance` decimal(10,3) NOT NULL,
  `silver_debit` decimal(10,3) NOT NULL,
  `silver_credit` decimal(10,3) NOT NULL,
  `silver_balance` decimal(10,3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_supplier_ledgers_seller_id` (`seller_id`),
  CONSTRAINT `supplier_ledgers_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_ledgers`
--

LOCK TABLES `supplier_ledgers` WRITE;
/*!40000 ALTER TABLE `supplier_ledgers` DISABLE KEYS */;
INSERT INTO `supplier_ledgers` VALUES (1,28,'2026-08-01 17:15:17','Purchase','PUR-516806','Purchase PUR-516806',0.00,1631.52,1631.52,0.000,0.000,0.000,0.000,0.000,0.000),(2,29,'2026-08-01 18:53:30','Purchase','PUR-409547','Purchase PUR-409547',0.00,925.36,925.36,0.000,0.000,0.000,0.000,0.000,0.000),(3,1,'2026-08-01 18:55:08','Payment','','xsvc',1200.00,100.00,38146.00,0.000,0.000,0.000,0.000,0.000,0.000),(4,30,'2026-08-01 19:50:49','Purchase','PUR-849236','Purchase PUR-849236',0.00,3089.95,3089.95,0.000,0.000,0.000,0.000,0.000,0.000),(5,31,'2026-08-02 03:52:00','Purchase','PUR-720178','Purchase PUR-720178',0.00,0.00,0.00,0.000,0.000,0.000,0.000,0.000,0.000),(6,31,'2026-08-02 04:01:27','Purchase','PUR-287061','Purchase PUR-287061',0.00,855.62,855.62,0.000,0.000,0.000,0.000,0.000,0.000),(7,31,'2026-08-02 04:01:27','Payment','PAY-PUR-287061','Payment for Purchase PUR-287061',300.62,0.00,555.00,0.000,0.000,0.000,0.000,0.000,0.000),(8,31,'2026-08-02 04:19:08','Purchase','PUR-347788','Purchase PUR-347788',0.00,11848.80,12403.80,0.000,0.000,0.000,0.000,0.000,0.000),(9,31,'2026-08-02 04:19:08','Payment','PAY-PUR-347788','Payment for Purchase PUR-347788',10000.07,0.00,2403.73,0.000,0.000,0.000,0.000,0.000,0.000),(10,30,'2026-08-02 05:58:23','Purchase','PUR-302936','Purchase PUR-302936',0.00,1053.70,4143.65,0.000,0.000,0.000,0.000,0.000,0.000),(11,30,'2026-08-02 05:58:23','Payment','PAY-PUR-302936','Payment for Purchase PUR-302936',500.00,0.00,3643.65,0.000,0.000,0.000,0.000,0.000,0.000),(12,13,'2026-08-02 06:10:15','Purchase','PUR-15289','Purchase PUR-15289',0.00,4924.96,28753.96,0.000,0.000,0.000,0.000,0.000,0.000),(13,13,'2026-08-02 06:10:15','Payment','PAY-PUR-15289','Payment for Purchase PUR-15289',4924.97,0.00,23828.99,0.000,0.000,0.000,0.000,0.000,0.000),(14,28,'2026-08-02 07:24:18','Purchase','PUR-458483','Purchase PUR-458483',0.00,0.00,1631.52,0.000,0.000,0.000,0.000,0.000,0.000),(15,28,'2026-08-02 07:24:18','Payment','PAY-PUR-458483','Payment for Purchase PUR-458483',291.72,0.00,1339.80,0.000,0.000,0.000,0.000,0.000,0.000),(16,28,'2026-08-02 07:32:56','Purchase','PUR-975630','Purchase PUR-975630',0.00,0.00,1339.80,0.000,0.000,0.000,0.000,0.000,0.000),(17,28,'2026-08-02 07:32:56','Payment','PAY-PUR-975630','Payment for Purchase PUR-975630',3812.76,0.00,-2472.96,0.000,0.000,0.000,0.000,0.000,0.000),(18,26,'2026-08-02 07:54:20','Purchase','PUR-259627','Purchase PUR-259627',0.00,59.74,59.74,0.000,0.000,0.000,0.000,0.000,0.000),(19,26,'2026-08-02 07:54:20','Payment','PAY-PUR-259627','Payment for Purchase PUR-259627',6144.88,0.00,-6085.14,0.000,0.000,0.000,0.000,0.000,0.000),(20,28,'2026-08-02 07:55:47','Purchase','PUR-346857','Purchase PUR-346857',0.00,103.00,-2369.96,0.000,0.000,0.000,0.000,0.000,0.000),(21,28,'2026-08-02 07:55:47','Payment','PAY-PUR-346857','Payment for Purchase PUR-346857',4913.50,0.00,-7283.46,0.000,0.000,0.000,0.000,0.000,0.000),(22,28,'2026-08-02 08:15:05','Purchase','PUR-505286','Purchase PUR-505286',0.00,3615.30,-3668.16,0.000,0.000,0.000,0.000,0.000,0.000),(23,28,'2026-08-02 08:15:05','Payment','PAY-PUR-505286','Payment for Purchase PUR-505286',3000.00,0.00,-6668.16,0.000,0.000,0.000,0.000,0.000,0.000);
/*!40000 ALTER TABLE `supplier_ledgers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `mobile` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL,
  `gst_number` varchar(20) DEFAULT NULL,
  `outstanding_balance` decimal(12,2) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_suppliers_mobile` (`mobile`),
  KEY `ix_suppliers_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `role_id` (`role_id`),
  KEY `ix_users_id` (`id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=338 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (197,'admin','admin@jewelleryerp.com','$2b$12$CPIKuDIcAoOc.7f/3uLeU.R9Px2XUaW7fFRu6z48OZHhzFdjKH7ju','Super Admin',1,155,'2026-07-31 19:25:12',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouses`
--

DROP TABLE IF EXISTS `warehouses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `location_address` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouses`
--

LOCK TABLES `warehouses` WRITE;
/*!40000 ALTER TABLE `warehouses` DISABLE KEYS */;
/*!40000 ALTER TABLE `warehouses` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-02 14:43:20
