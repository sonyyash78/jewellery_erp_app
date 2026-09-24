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
INSERT INTO `alembic_version` VALUES ('a48d02fb554c');
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
  KEY `ix_audit_logs_entity_id` (`entity_id`),
  KEY `ix_audit_logs_entity_name` (`entity_name`),
  KEY `ix_audit_logs_timestamp` (`timestamp`),
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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `is_default` tinyint(1) NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_ledgers`
--

LOCK TABLES `customer_ledgers` WRITE;
/*!40000 ALTER TABLE `customer_ledgers` DISABLE KEYS */;
INSERT INTO `customer_ledgers` VALUES (1,2,'2026-08-06 05:26:01','Invoice','INV-20260806-0001','Sales Bill INV-20260806-0001',42.00,0.00,42.00,0.000,0.000,0.000,45.000,0.000,45.000),(2,2,'2026-08-06 05:26:01','Payment','INV-20260806-0001','Payment for INV-20260806-0001',0.00,42.00,0.00,0.000,0.000,0.000,0.000,0.000,45.000),(3,2,'2026-08-06 06:04:46','Invoice','INV-20260806-0002','Sales Bill INV-20260806-0002',793.00,0.00,793.00,0.000,0.000,0.000,0.000,0.000,45.000),(4,2,'2026-08-06 06:04:46','Payment','INV-20260806-0002','Payment for INV-20260806-0002',0.00,700.00,93.00,0.000,0.000,0.000,0.000,0.000,45.000),(5,2,'2026-08-06 06:19:41','Invoice','INV-20260806-0003','Sales Bill INV-20260806-0003',0.00,0.00,93.00,0.000,0.000,0.000,83.000,0.000,128.000),(6,2,'2026-08-06 12:06:09','Invoice','INV-20260806-0004','Sales Bill INV-20260806-0004',0.00,0.00,93.00,0.000,0.000,0.000,70.000,0.000,198.000),(7,2,'2026-08-06 12:34:23','Invoice','INV-20260806-0005','Sales Bill INV-20260806-0005',124.00,0.00,217.00,0.000,0.000,0.000,0.000,0.000,198.000),(8,2,'2026-08-06 12:34:23','Payment','INV-20260806-0005','Payment for INV-20260806-0005',0.00,120.00,97.00,0.000,0.000,0.000,0.000,0.000,198.000),(9,2,'2026-08-06 12:38:44','Invoice','INV-20260806-0006','Sales Bill INV-20260806-0006',3090.00,0.00,3187.00,0.000,0.000,0.000,70.000,0.000,268.000),(10,2,'2026-08-06 12:38:44','Payment','INV-20260806-0006','Payment for INV-20260806-0006',0.00,3090.00,97.00,0.000,0.000,0.000,0.000,0.000,268.000),(11,3,'2026-08-06 12:46:51','Invoice','INV-20260806-0007','Sales Bill INV-20260806-0007',0.00,0.00,0.00,0.000,0.000,0.000,0.000,0.000,0.000),(12,2,'2026-08-06 14:32:04','Invoice','INV-20260806-0008','Sales Bill INV-20260806-0008',57.00,0.00,154.00,100.000,0.000,100.000,0.000,0.000,268.000),(13,2,'2026-08-06 14:32:04','Payment','INV-20260806-0008','Payment for INV-20260806-0008',0.00,50.00,104.00,0.000,0.000,100.000,0.000,0.000,268.000),(14,3,'2026-08-06 15:43:48','Invoice','INV-20260806-0009','Sales Bill INV-20260806-0009',206.00,0.00,206.00,0.000,0.000,0.000,143.000,0.000,143.000),(15,3,'2026-08-06 15:43:48','Payment','INV-20260806-0009','Payment for INV-20260806-0009',0.00,206.00,0.00,0.000,0.000,0.000,0.000,0.000,143.000),(16,2,'2026-08-06 15:56:35','Invoice','INV-20260806-0010','Sales Bill INV-20260806-0010',347.00,0.00,451.00,159.000,0.000,259.000,97.000,0.000,365.000),(17,2,'2026-08-06 15:56:35','Payment','INV-20260806-0010','Payment for INV-20260806-0010',0.00,300.00,151.00,0.000,0.000,259.000,0.000,0.000,365.000),(18,2,'2026-08-07 08:03:01','Invoice','INV-20260807-0001','Sales Bill INV-20260807-0001',52.00,0.00,203.00,147.000,0.000,406.000,0.000,0.000,365.000),(19,2,'2026-08-07 08:03:01','Payment','INV-20260807-0001','Payment for INV-20260807-0001',0.00,50.00,153.00,0.000,0.000,406.000,0.000,0.000,365.000),(20,3,'2026-08-07 08:05:56','Invoice','INV-20260807-0002','Sales Bill INV-20260807-0002',160.00,0.00,160.00,166.000,0.000,166.000,1420.000,0.000,1563.000),(21,3,'2026-08-07 08:05:56','Payment','INV-20260807-0002','Payment for INV-20260807-0002',0.00,60.00,100.00,0.000,0.000,166.000,0.000,0.000,1563.000),(22,3,'2026-08-10 04:08:01','Exchange','EXC-1','Exchange Difference Settlement',164171.70,0.00,164271.70,22.000,15.000,173.000,0.000,0.000,1563.000),(23,3,'2026-08-10 04:08:01','Payment','PAY-EXC-1','Payment for Exchange EXC-1',0.00,164171.70,100.00,0.000,0.000,173.000,0.000,0.000,1563.000),(24,18,'2026-08-10 05:59:15','Invoice','INV-20260810-0001','Sales Bill INV-20260810-0001',0.00,0.00,0.00,0.000,0.000,0.000,125.000,0.000,125.000),(25,3,'2026-08-28 04:58:11','Invoice','INV-20260828-0001','Sales Bill INV-20260828-0001',0.00,0.00,100.00,4.140,0.000,177.140,0.000,0.000,1563.000),(26,3,'2026-08-28 15:09:54','Invoice','INV-20260828-0002','Sales Bill INV-20260828-0002',149247.00,0.00,149347.00,-6.320,0.000,170.820,0.000,0.000,1563.000),(27,3,'2026-08-28 15:09:54','Payment','INV-20260828-0002','Payment for INV-20260828-0002',0.00,49247.00,100100.00,0.000,0.000,170.820,0.000,0.000,1563.000),(28,2,'2026-08-28 16:06:37','Invoice','INV-20260828-0003','Sales Bill INV-20260828-0003',22763.00,0.00,22916.00,0.000,0.000,406.000,-15.000,0.000,350.000),(29,2,'2026-08-28 16:06:37','Payment','INV-20260828-0003','Payment for INV-20260828-0003',0.00,12000.00,10916.00,0.000,0.000,406.000,0.000,0.000,350.000),(30,2,'2026-08-28 16:20:21','Invoice','INV-20260828-0004','Sales Bill INV-20260828-0004',43775.00,0.00,54691.00,0.000,0.000,406.000,-50.000,0.000,300.000),(31,2,'2026-08-28 16:20:21','Payment','INV-20260828-0004','Payment for INV-20260828-0004',0.00,20000.00,34691.00,0.000,0.000,406.000,0.000,0.000,300.000),(32,18,'2026-09-19 12:57:31','Invoice','INV-20260919-0001','Sales Bill INV-20260919-0001',0.00,0.00,0.00,43.600,0.000,43.600,0.000,0.000,125.000),(33,3,'2026-09-19 13:03:27','Invoice','INV-20260919-0002','Sales Bill INV-20260919-0002',0.00,0.00,100100.00,0.000,0.000,170.820,31.000,0.000,1594.000),(34,18,'2026-09-19 15:33:50','Invoice','INV-20260919-0003','Hybrid Bill INV-20260919-0003 (Settled in Metal)',9270.00,9270.00,0.00,0.000,0.000,43.600,60.778,0.000,185.778),(35,3,'2026-09-19 15:42:47','Invoice','INV-20260919-0004','Hybrid Bill INV-20260919-0004 (Settled in Metal)',0.00,0.00,100100.00,9.520,0.000,180.340,0.000,0.000,1594.000),(36,2,'2026-09-19 15:47:41','Invoice','INV-20260919-0005','Hybrid Bill INV-20260919-0005 (Settled in Metal)',4223.00,4223.00,34691.00,0.000,0.000,406.000,0.000,0.000,300.000),(37,2,'2026-09-19 16:07:07','Invoice','INV-20260919-0006','Hybrid Bill INV-20260919-0006 (Settled in Cash)',12875.00,10000.00,37566.00,0.000,0.000,406.000,0.000,0.000,300.000),(38,3,'2026-09-19 16:08:37','Invoice','INV-20260919-0007','Hybrid Bill INV-20260919-0007 (Settled in Metal)',12875.00,12875.00,100100.00,0.000,0.000,180.340,11.500,0.000,1605.500),(39,18,'2026-09-19 16:29:26','Invoice','INV-20260919-0008','Hybrid Bill INV-20260919-0008 (Settled in Metal)',12875.00,12875.00,0.00,0.000,0.000,43.600,10.500,0.000,196.278),(40,3,'2026-09-19 16:37:47','Invoice','INV-20260919-0009','Hybrid Bill INV-20260919-0009 (Settled in Metal)',25750.00,25750.00,100100.00,0.000,0.000,180.340,25.000,0.000,1630.500),(41,18,'2026-09-19 16:44:16','Invoice','INV-20260919-0010','Hybrid Bill INV-20260919-0010 (Settled in Cash)',5150.00,3500.00,1650.00,0.000,0.000,43.600,0.000,0.000,196.278),(42,19,'2026-09-19 16:48:07','Invoice','INV-20260919-0011','Hybrid Bill INV-20260919-0011 (Settled in Cash)',5150.00,3500.00,1650.00,0.000,0.000,0.000,0.000,0.000,0.000),(43,18,'2026-09-19 16:51:25','Invoice','INV-20260919-0012','Hybrid Bill INV-20260919-0012 (Settled in Metal)',2575.00,2575.00,1650.00,0.000,0.000,43.600,3.300,0.000,199.578),(44,18,'2026-09-19 17:27:48','Invoice','INV-20260919-0013','Hybrid Bill INV-20260919-0013 (Settled in Metal)',8240.00,8240.00,1650.00,0.481,0.000,44.081,0.000,0.000,199.578),(45,18,'2026-09-19 17:41:59','Invoice','INV-20260919-0014','Hybrid Bill INV-20260919-0014 (Settled in Cash)',18167.00,0.00,19817.00,0.000,0.000,44.081,0.000,0.000,199.578),(46,2,'2026-09-19 17:44:01','Invoice','INV-20260919-0015','Hybrid Bill INV-20260919-0015 (Settled in Metal)',7725.00,7725.00,37566.00,0.000,0.000,406.000,7.900,0.000,307.900),(47,3,'2026-09-19 17:45:14','Invoice','INV-20260919-0016','Hybrid Bill INV-20260919-0016 (Settled in Metal)',8652.00,8652.00,100100.00,0.000,0.000,180.340,8.608,0.000,1639.108),(48,18,'2026-09-19 17:50:58','Invoice','INV-20260919-0017','Hybrid Bill INV-20260919-0017 (Settled in Metal)',1823.00,1823.00,19817.00,0.000,0.000,44.081,15.256,0.000,214.834),(49,3,'2026-09-19 18:00:51','Invoice','INV-20260919-0018','Hybrid Bill INV-20260919-0018 (Settled in Metal)',14132.00,14132.00,100100.00,15.184,0.000,195.524,15.867,0.000,1654.975),(50,3,'2026-09-19 18:27:19','Invoice','INV-20260919-0019','Hybrid Bill INV-20260919-0019 (Settled in Metal)',5150.00,5150.00,100100.00,0.000,0.000,195.524,4.000,0.000,1658.975),(51,19,'2026-09-20 05:03:46','Invoice','INV-20260920-0001','Hybrid Bill INV-20260920-0001 (Settled in Metal)',1205.00,1205.00,1650.00,0.000,0.000,0.000,4.833,0.000,4.833),(52,18,'2026-09-20 05:05:30','Invoice','INV-20260920-0002','Hybrid Bill INV-20260920-0002 (Settled in Metal)',34201.00,34201.00,19817.00,16.484,0.000,60.565,0.000,0.000,214.834),(53,2,'2026-09-20 05:15:38','Invoice','INV-20260920-0003','Hybrid Bill INV-20260920-0003 (Settled in Metal)',1823.00,1823.00,37566.00,0.000,0.000,406.000,9.700,0.000,317.600),(54,3,'2026-09-20 05:17:49','Invoice','INV-20260920-0004','Hybrid Bill INV-20260920-0004 (Settled in Cash)',0.00,0.00,100100.00,0.000,0.000,195.524,12.000,0.000,1670.975),(55,3,'2026-09-20 05:27:23','Invoice','INV-20260920-0005','Hybrid Bill INV-20260920-0005 (Settled in Cash)',0.00,0.00,100100.00,0.000,0.000,195.524,5.800,0.000,1676.775),(56,3,'2026-09-20 05:28:19','Invoice','INV-20260920-0006','Hybrid Bill INV-20260920-0006 (Settled in Metal)',6345.00,6345.00,100100.00,0.000,0.000,195.524,8.380,0.000,1685.155),(57,18,'2026-09-20 08:09:03','Invoice','INV-20260920-0007','Hybrid Bill INV-20260920-0007 (Settled in Metal)',17770.00,17770.00,19817.00,10.131,0.000,70.696,0.000,0.000,214.834),(58,18,'2026-09-20 08:20:05','Invoice','INV-20260920-0008','Hybrid Bill INV-20260920-0008 (Settled in Cash)',38151.00,38151.00,19817.00,0.000,0.000,70.696,0.000,0.000,214.834),(59,19,'2026-09-20 08:38:08','Invoice','INV-20260920-0009','Hybrid Bill INV-20260920-0009 (Settled in Metal)',44640.00,44640.00,1650.00,10.520,0.000,10.520,32.500,0.000,37.333),(60,18,'2026-09-20 15:19:44','Exchange','EXC-2','Exchange 2 (Settled in Cash)',274282.86,0.00,294099.86,0.000,0.000,70.696,0.000,0.000,214.834),(61,3,'2026-09-21 04:19:23','Invoice','INV-20260921-0001','Hybrid Bill INV-20260921-0001 (Settled in Metal)',76132.00,76132.00,100100.00,4.160,0.000,199.684,3.500,0.000,1688.655),(62,3,'2026-09-21 07:02:35','Invoice','INV-20260921-0002','Hybrid Bill INV-20260921-0002 (Settled in Metal)',276622.00,276622.00,100100.00,36.640,0.000,236.324,32.500,0.000,1721.155),(63,18,'2026-09-21 07:19:34','Invoice','INV-20260921-0003','Hybrid Bill INV-20260921-0003 (Settled in Metal)',136928.00,136928.00,294099.86,10.320,0.000,81.016,0.000,0.000,214.834),(64,2,'2026-09-21 07:21:22','Invoice','INV-20260921-0004','Hybrid Bill INV-20260921-0004 (Settled in Metal)',138133.00,138133.00,37566.00,6.320,0.000,412.320,8.000,0.000,325.600);
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
  `gst_number` varchar(50) DEFAULT NULL,
  `credit_limit` decimal(12,2) DEFAULT NULL,
  `outstanding_balance` decimal(12,2) DEFAULT NULL,
  `fine_gold_balance` decimal(10,3) DEFAULT NULL,
  `fine_silver_balance` decimal(10,3) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_customers_phone_number` (`phone_number`),
  UNIQUE KEY `ix_customers_email` (`email`),
  KEY `ix_customers_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (2,'yash','','1234567894',NULL,'','',NULL,NULL,NULL,NULL,0.00,37566.00,412.320,325.600,1,0,'2026-08-06 10:55:35','2026-09-21 12:51:22'),(3,'nilesh','','8504837854',NULL,'','raj',NULL,NULL,'','',0.00,100100.00,236.324,1721.155,1,0,'2026-08-06 18:16:49','2026-09-21 12:32:35'),(18,'vansh','','7777777777',NULL,'','',NULL,NULL,NULL,NULL,0.00,294099.86,81.016,214.834,1,0,'2026-08-10 11:29:12','2026-09-21 12:49:34'),(19,'soni','','1212121121',NULL,'','',NULL,NULL,NULL,NULL,0.00,1650.00,10.520,37.333,1,0,'2026-09-19 22:18:04','2026-09-20 14:08:08'),(20,'nilu',NULL,'7894561231',NULL,NULL,'pali',NULL,NULL,'','',0.00,0.00,0.000,0.000,1,0,'2026-09-21 12:52:41',NULL);
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
  `wastage` decimal(5,2) NOT NULL,
  `fine_weight` decimal(10,3) NOT NULL,
  `labour_charge` decimal(10,2) NOT NULL,
  `testing_melting_charge` decimal(10,2) NOT NULL,
  `hallmark_charge` decimal(10,2) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exchange_id` (`exchange_id`),
  CONSTRAINT `exchange_items_ibfk_1` FOREIGN KEY (`exchange_id`) REFERENCES `exchanges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_items`
--

LOCK TABLES `exchange_items` WRITE;
/*!40000 ALTER TABLE `exchange_items` DISABLE KEYS */;
INSERT INTO `exchange_items` VALUES (1,1,'Old Gold Deposit','Gold','24K',100.00,15.000,0.000,15.000,0.00,0.00,0.00,15.000,0.00,0.00,0.00,0.00,0.00);
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
  `stock_item_id` int DEFAULT NULL,
  `item_name` varchar(100) NOT NULL,
  `metal` varchar(50) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `touch_purity` decimal(5,2) NOT NULL,
  `wastage` decimal(5,2) NOT NULL,
  `fine_weight` decimal(10,3) NOT NULL,
  `making_charge_type` varchar(20) NOT NULL,
  `making_charge_rate` decimal(10,2) NOT NULL,
  `making_charges_amount` decimal(10,2) NOT NULL,
  `hallmark_charges` decimal(10,2) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  `rate_applied` decimal(10,2) NOT NULL,
  `final_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exchange_id` (`exchange_id`),
  KEY `stock_item_id` (`stock_item_id`),
  CONSTRAINT `exchange_new_items_ibfk_1` FOREIGN KEY (`exchange_id`) REFERENCES `exchanges` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exchange_new_items_ibfk_2` FOREIGN KEY (`stock_item_id`) REFERENCES `stock_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_new_items`
--

LOCK TABLES `exchange_new_items` WRITE;
/*!40000 ALTER TABLE `exchange_new_items` DISABLE KEYS */;
INSERT INTO `exchange_new_items` VALUES (1,1,2,'coin','Gold',100.000,100.000,0.000,22.00,0.00,22.000,'flat',0.00,0.00,0.00,0.00,0.00,7245.00,159390.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchanges`
--

LOCK TABLES `exchanges` WRITE;
/*!40000 ALTER TABLE `exchanges` DISABLE KEYS */;
INSERT INTO `exchanges` VALUES (1,3,'2026-08-10 09:38:01',0.00,159390.00,4781.70,164171.70,164171.70),(2,18,'2026-09-20 20:49:43',75524.20,339618.50,10188.56,349807.06,274282.86);
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
  `applied_rate` decimal(10,2) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `stone_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `making_charge_type` varchar(20) NOT NULL,
  `making_charge_rate` decimal(10,2) NOT NULL,
  `making_charges_amount` decimal(10,2) NOT NULL,
  `hallmark_charges` decimal(10,2) NOT NULL,
  `total_gold_value` decimal(12,2) NOT NULL,
  `touch_purity` decimal(5,2) NOT NULL,
  `wastage` decimal(5,2) NOT NULL,
  `fine_weight` decimal(10,3) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_item_id` (`invoice_item_id`),
  KEY `metal_rate_id` (`metal_rate_id`),
  CONSTRAINT `gold_calculations_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `gold_calculations_ibfk_2` FOREIGN KEY (`metal_rate_id`) REFERENCES `gold_rates` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gold_calculations`
--

LOCK TABLES `gold_calculations` WRITE;
/*!40000 ALTER TABLE `gold_calculations` DISABLE KEYS */;
INSERT INTO `gold_calculations` VALUES (1,2,NULL,0.00,45.000,0.000,45.000,'flat',0.00,650.00,120.00,0.00,0.00,0.00,0.000,0.00,0.00),(2,8,NULL,0.00,100.000,0.000,100.000,'flat',0.00,0.00,120.00,0.00,0.00,0.00,0.000,0.00,0.00),(3,10,NULL,0.00,100.000,0.000,100.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000,0.00,0.00),(4,11,NULL,0.00,100.000,0.000,100.000,'flat',0.00,55.00,100.00,0.00,100.00,0.00,100.000,0.00,0.00),(5,23,NULL,0.00,100.000,0.000,100.000,'flat',0.00,100.00,0.00,0.00,77.00,8.00,85.000,0.00,0.00),(6,25,NULL,0.00,74.000,0.000,74.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,74.000,0.00,0.00),(7,27,NULL,0.00,100.000,0.000,100.000,'flat',0.00,100.00,0.00,0.00,77.00,0.00,77.000,0.00,0.00),(8,28,NULL,0.00,70.000,0.000,70.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,70.000,0.00,0.00),(9,29,NULL,0.00,100.000,0.000,100.000,'flat',0.00,0.00,120.00,0.00,78.00,8.00,86.000,0.00,0.00),(10,31,NULL,0.00,80.000,0.000,80.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,80.000,0.00,0.00),(11,37,NULL,0.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,0.00,91.60,4.10,19.140,0.00,0.00),(12,38,NULL,0.00,15.000,0.000,15.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,15.000,0.00,0.00),(13,39,NULL,7245.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,132728.40,91.60,0.00,18.320,0.00,0.00),(14,40,NULL,0.00,6.320,0.000,6.320,'flat',0.00,0.00,0.00,0.00,100.00,0.00,6.320,0.00,0.00),(15,45,NULL,0.00,100.000,0.000,100.000,'flat',0.00,0.00,0.00,0.00,91.60,2.00,93.600,0.00,0.00),(16,46,NULL,0.00,50.000,0.000,50.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,50.000,0.00,0.00),(17,51,NULL,0.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,0.00,91.60,6.00,19.520,0.00,0.00),(18,52,NULL,0.00,10.000,0.000,10.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,10.000,0.00,0.00),(20,72,NULL,150.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,3000.00,100.00,0.00,20.000,0.00,0.00),(21,74,NULL,150.00,15.000,0.000,15.000,'flat',0.00,0.00,0.00,2250.00,100.00,0.00,15.000,0.00,0.00),(22,76,NULL,150.00,20.000,0.000,20.000,'flat',0.00,13000.00,120.00,2748.00,91.60,0.00,18.320,0.00,0.00),(23,84,NULL,0.00,20.000,0.000,20.000,'flat',0.00,13000.00,120.00,0.00,91.60,0.00,18.320,0.00,0.00),(24,86,NULL,0.00,5.000,0.000,5.000,'flat',0.00,0.00,0.00,0.00,100.00,0.00,5.000,0.00,0.00),(25,92,NULL,725.00,50.000,0.000,50.000,'flat',0.00,0.00,0.00,33205.00,91.60,0.00,45.800,0.00,0.00),(26,93,NULL,725.00,10.000,0.000,10.000,'flat',0.00,0.00,0.00,7250.00,100.00,0.00,10.000,0.00,0.00),(27,102,NULL,725.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,13427.00,91.60,1.00,18.520,0.00,0.00),(28,104,NULL,725.00,5.000,0.000,5.000,'flat',0.00,0.00,0.00,3625.00,100.00,0.00,5.000,0.00,0.00),(29,106,NULL,2000.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,37040.00,91.60,1.00,18.520,0.00,0.00),(30,107,NULL,2000.00,1.570,0.000,1.570,'flat',0.00,0.00,0.00,3140.00,100.00,0.00,1.570,0.00,0.00),(31,109,NULL,2000.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,37040.00,91.60,1.00,18.520,0.00,0.00),(32,110,NULL,2000.00,10.000,0.000,10.000,'flat',0.00,0.00,0.00,16000.00,80.00,0.00,8.000,0.00,0.00),(33,112,NULL,72500.00,10.000,0.000,10.000,'flat',0.00,6500.00,120.00,66410.00,91.60,0.00,9.160,0.00,0.00),(34,114,NULL,72500.00,5.000,0.000,5.000,'flat',0.00,0.00,0.00,36250.00,100.00,0.00,5.000,0.00,0.00),(35,116,NULL,72500.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,132820.00,91.60,0.00,18.320,0.00,0.00),(36,119,NULL,72500.00,20.000,0.000,20.000,'flat',0.00,0.00,0.00,132820.00,91.60,0.00,18.320,0.00,0.00),(37,120,NULL,72500.00,20.000,0.000,20.000,'flat',0.00,0.00,120.00,132820.00,91.60,0.00,18.320,0.00,0.00),(38,121,NULL,72500.00,8.000,0.000,8.000,'flat',0.00,0.00,0.00,58000.00,100.00,0.00,8.000,0.00,0.00),(39,122,NULL,72500.00,20.000,0.000,20.000,'flat',0.00,0.00,120.00,132820.00,91.60,0.00,18.320,0.00,0.00),(40,124,NULL,72500.00,12.000,0.000,12.000,'flat',0.00,0.00,0.00,87000.00,100.00,0.00,12.000,0.00,0.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `rate_per_gram` decimal(10,2) NOT NULL,
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
  `item_code` varchar(20) NOT NULL,
  `category_id` int DEFAULT NULL,
  `metal_type` enum('GOLD','SILVER') NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `net_weight` decimal(10,3) NOT NULL,
  `purity` varchar(20) DEFAULT NULL,
  `touch` decimal(5,2) DEFAULT NULL,
  `design_code` varchar(50) DEFAULT NULL,
  `status` enum('AVAILABLE','SOLD','RESERVED') DEFAULT NULL,
  `qr_code_id` int DEFAULT NULL,
  `qr_image_path` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_inventory_item_code` (`item_code`),
  UNIQUE KEY `qr_code_id` (`qr_code_id`),
  KEY `category_id` (`category_id`),
  KEY `ix_inventory_id` (`id`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`qr_code_id`) REFERENCES `qr_inventory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  KEY `product_variant_id` (`product_variant_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `ix_inventory_items_status` (`status`),
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
  KEY `invoice_id` (`invoice_id`),
  KEY `inventory_item_id` (`inventory_item_id`),
  CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`inventory_item_id`) REFERENCES `inventory_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_items`
--

LOCK TABLES `invoice_items` WRITE;
/*!40000 ALTER TABLE `invoice_items` DISABLE KEYS */;
INSERT INTO `invoice_items` VALUES (1,1,NULL,'1','SILVER',40.50),(2,2,NULL,'Gold Item','GOLD',770.00),(6,6,NULL,'Silver Item','SILVER',0.00),(7,7,NULL,'chain','SILVER',0.00),(8,8,NULL,'chain','GOLD',120.00),(9,9,NULL,'coin','SILVER',3000.00),(10,10,NULL,'coin','GOLD',0.00),(11,11,NULL,'chain','GOLD',55.00),(21,21,NULL,'payal','SILVER',200.00),(22,21,NULL,'Old Silver Deposit','SILVER',0.00),(23,22,NULL,'coin','GOLD',87.00),(24,22,NULL,'coin','SILVER',250.00),(25,22,NULL,'Old Gold Deposit','GOLD',0.00),(26,22,NULL,'Old Silver Deposit','SILVER',0.00),(27,23,NULL,'coin','GOLD',50.00),(28,23,NULL,'Old Gold Deposit','GOLD',0.00),(29,24,NULL,'coin','GOLD',75.00),(30,24,NULL,'coin','SILVER',80.00),(31,24,NULL,'Old Gold Deposit','GOLD',0.00),(32,24,NULL,'Old Silver Deposit','SILVER',0.00),(33,25,NULL,'coin','SILVER',0.00),(34,25,NULL,'Old Silver Deposit','SILVER',0.00),(35,26,NULL,'coin','SILVER',0.00),(36,26,NULL,'Old Silver Deposit','SILVER',0.00),(37,27,NULL,'coin','GOLD',0.00),(38,27,NULL,'Old Gold Deposit','GOLD',0.00),(39,28,NULL,'coin','GOLD',144900.00),(40,28,NULL,'Old Gold Deposit','GOLD',0.00),(41,29,NULL,'chain','SILVER',22100.00),(42,29,NULL,'Old Silver Deposit','SILVER',0.00),(43,30,NULL,'chain','SILVER',42500.00),(44,30,NULL,'Old Silver Deposit','SILVER',0.00),(45,31,NULL,'chain','GOLD',0.00),(46,31,NULL,'Old Gold Deposit','GOLD',0.00),(47,32,NULL,'payall','SILVER',0.00),(48,32,NULL,'Old Silver Deposit','SILVER',0.00),(49,33,NULL,'payall','SILVER',9000.00),(50,33,NULL,'Old Silver Deposit','SILVER',0.00),(51,34,NULL,'coin','GOLD',0.00),(52,34,NULL,'Old Gold Deposit','GOLD',0.00),(53,35,NULL,'coin','SILVER',4100.00),(54,35,NULL,'Old Silver Deposit','SILVER',0.00),(55,36,NULL,'payal','SILVER',12500.00),(56,36,NULL,'Old Silver Deposit','SILVER',0.00),(57,37,NULL,'pyal','SILVER',12500.00),(58,37,NULL,'Old Silver Deposit','SILVER',0.00),(59,38,NULL,'coin','SILVER',12500.00),(60,38,NULL,'Old Silver Deposit','SILVER',0.00),(61,39,NULL,'coin','SILVER',25000.00),(62,39,NULL,'Old Silver Deposit','SILVER',0.00),(63,40,NULL,'coin','SILVER',5000.00),(64,40,NULL,'Old Silver Deposit','SILVER',0.00),(65,41,NULL,'coin','SILVER',5000.00),(66,41,NULL,'Old Silver Deposit','SILVER',0.00),(67,42,NULL,'coin','SILVER',2500.00),(68,42,NULL,'Old Silver Deposit','SILVER',0.00),(72,44,NULL,'co','GOLD',3000.00),(73,44,NULL,'co','SILVER',5000.00),(74,44,NULL,'Old Gold Deposit','GOLD',0.00),(75,44,NULL,'Old Silver Deposit','SILVER',0.00),(76,45,NULL,'c','GOLD',15868.00),(77,45,NULL,'c','SILVER',1770.00),(78,46,NULL,'coin','SILVER',7500.00),(79,46,NULL,'Old Silver Deposit','SILVER',0.00),(80,47,NULL,'coin','SILVER',8400.00),(81,47,NULL,'Old Silver Deposit','SILVER',0.00),(82,48,NULL,'coim','SILVER',1770.00),(83,48,NULL,'Old Silver Deposit','SILVER',0.00),(84,49,NULL,'Gold Item','GOLD',13120.00),(85,49,NULL,'Silver Item','SILVER',600.00),(86,49,NULL,'Old Gold Deposit','GOLD',0.00),(87,49,NULL,'Old Silver Deposit','SILVER',0.00),(88,50,NULL,'coin','SILVER',5000.00),(89,50,NULL,'Old Silver Deposit','SILVER',0.00),(90,51,NULL,'coin','SILVER',1170.00),(91,51,NULL,'Old Silver Deposit','SILVER',0.00),(92,52,NULL,'coin','GOLD',33205.00),(93,52,NULL,'Old Gold Deposit','GOLD',0.00),(94,53,NULL,'coin','SILVER',1770.00),(95,53,NULL,'Old Silver Deposit','SILVER',0.00),(96,54,NULL,'coin ','SILVER',0.00),(97,54,NULL,'Old Silver Deposit','SILVER',0.00),(98,55,NULL,'coin','SILVER',0.00),(99,55,NULL,'Old Silver Deposit','SILVER',0.00),(100,56,NULL,'coin','SILVER',6160.00),(101,56,NULL,'Old Silver Deposit','SILVER',0.00),(102,57,NULL,'c','GOLD',13427.00),(103,57,NULL,'c','SILVER',3825.00),(104,57,NULL,'Old Gold Deposit','GOLD',0.00),(105,57,NULL,'Old Silver Deposit','SILVER',0.00),(106,58,NULL,'c','GOLD',37040.00),(107,58,NULL,'Old Gold Deposit','GOLD',0.00),(108,59,NULL,'c','SILVER',6300.00),(109,59,NULL,'c','GOLD',37040.00),(110,59,NULL,'Old Gold Deposit','GOLD',0.00),(111,59,NULL,'Old Silver Deposit','SILVER',0.00),(112,60,NULL,'Gold Item','GOLD',73030.00),(113,60,NULL,'Silver Item','SILVER',885.00),(114,60,NULL,'Old Gold Deposit','GOLD',0.00),(115,60,NULL,'Old Silver Deposit','SILVER',0.00),(116,61,NULL,'Gold Item','GOLD',132820.00),(117,61,NULL,'Silver Item','SILVER',1170.00),(118,61,NULL,'Silver Item','SILVER',1755.00),(119,61,NULL,'Gold Item','GOLD',132820.00),(120,62,NULL,'Gold Item','GOLD',132940.00),(121,62,NULL,'Old Gold Deposit','GOLD',0.00),(122,63,NULL,'Gold Item','GOLD',132940.00),(123,63,NULL,'Silver Item','SILVER',1170.00),(124,63,NULL,'Old Gold Deposit','GOLD',0.00),(125,63,NULL,'Old Silver Deposit','SILVER',0.00);
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
  `status` enum('Draft','Partial','Paid','Completed','Cancelled') NOT NULL,
  `created_by` int NOT NULL,
  `bill_type` enum('Cash','Metal','Hybrid') NOT NULL,
  `settlement_type` enum('Cash','Metal') NOT NULL,
  `metal_received_value` decimal(12,2) NOT NULL,
  `cash_received` decimal(12,2) NOT NULL,
  `balance_amount` decimal(12,2) NOT NULL,
  `balance_metal_weight` decimal(12,3) NOT NULL,
  `settlement_metal_type` enum('Gold','Silver') DEFAULT NULL,
  `gold_balance_metal_weight` decimal(12,3) DEFAULT NULL,
  `silver_balance_metal_weight` decimal(12,3) DEFAULT NULL,
  `metal_received_str` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_invoices_invoice_number` (`invoice_number`),
  KEY `customer_id` (`customer_id`),
  KEY `created_by` (`created_by`),
  KEY `ix_invoices_invoice_date` (`invoice_date`),
  KEY `ix_invoices_status` (`status`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (1,2,'INV-20260806-0001','2026-08-06 10:56:01',40.50,1.21,0.00,42.00,'Cancelled',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(2,2,'INV-20260806-0002','2026-08-06 11:34:46',770.00,23.10,0.00,793.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(6,2,'INV-20260806-0003','2026-08-06 11:49:40',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(7,2,'INV-20260806-0004','2026-08-06 17:36:09',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(8,2,'INV-20260806-0005','2026-08-06 18:04:23',120.00,3.60,0.00,124.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(9,2,'INV-20260806-0006','2026-08-06 18:08:43',3000.00,90.00,0.00,3090.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(10,3,'INV-20260806-0007','2026-08-06 18:16:50',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(11,2,'INV-20260806-0008','2026-08-06 20:02:03',55.00,1.65,0.00,57.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(21,3,'INV-20260806-0009','2026-08-06 21:13:48',200.00,6.00,0.00,206.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(22,2,'INV-20260806-0010','2026-08-06 21:26:34',337.00,10.11,0.00,347.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(23,2,'INV-20260807-0001','2026-08-07 13:33:01',50.00,1.50,0.00,52.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(24,3,'INV-20260807-0002','2026-08-07 13:35:56',155.00,4.65,0.00,160.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(25,18,'INV-20260810-0001','2026-08-10 11:29:14',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(26,NULL,'INV-20260810-0002','2026-08-10 13:50:00',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(27,3,'INV-20260828-0001','2026-08-28 10:28:11',0.00,0.00,0.00,0.00,'Paid',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(28,3,'INV-20260828-0002','2026-08-28 20:39:53',144900.00,4347.00,0.00,149247.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(29,2,'INV-20260828-0003','2026-08-28 21:36:37',22100.00,663.00,0.00,22763.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(30,2,'INV-20260828-0004','2026-08-28 21:50:20',42500.00,1275.00,0.00,43775.00,'Completed',1,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(31,18,'INV-20260919-0001','2026-09-19 18:27:30',0.00,0.00,0.00,0.00,'Paid',88,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(32,3,'INV-20260919-0002','2026-09-19 18:33:26',0.00,0.00,0.00,0.00,'Paid',88,'Cash','Cash',0.00,0.00,0.00,0.000,NULL,NULL,NULL,NULL),(33,18,'INV-20260919-0003','2026-09-19 21:03:49',9000.00,270.00,0.00,9270.00,'Completed',88,'Hybrid','Metal',1800.00,2000.00,5470.00,60.778,'Silver',NULL,NULL,NULL),(34,3,'INV-20260919-0004','2026-09-19 21:12:46',0.00,0.00,0.00,0.00,'Paid',88,'Metal','Metal',0.00,0.00,0.00,0.000,'Gold',NULL,NULL,NULL),(35,2,'INV-20260919-0005','2026-09-19 21:17:40',4100.00,123.00,0.00,4223.00,'Completed',88,'Hybrid','Metal',500.00,100.00,3623.00,0.000,'Gold',NULL,NULL,NULL),(36,2,'INV-20260919-0006','2026-09-19 21:37:06',12500.00,375.00,0.00,12875.00,'Completed',88,'Hybrid','Cash',5000.00,5000.00,2875.00,0.000,NULL,NULL,NULL,NULL),(37,3,'INV-20260919-0007','2026-09-19 21:38:36',12500.00,375.00,0.00,12875.00,'Completed',88,'Hybrid','Metal',5000.00,5000.00,2875.00,11.500,'Silver',NULL,NULL,NULL),(38,18,'INV-20260919-0008','2026-09-19 21:59:26',12500.00,375.00,0.00,12875.00,'Completed',88,'Hybrid','Metal',6250.00,4000.00,2625.00,10.500,'Silver',NULL,NULL,NULL),(39,3,'INV-20260919-0009','2026-09-19 22:07:46',25000.00,750.00,0.00,25750.00,'Completed',88,'Metal','Metal',12500.00,7000.00,6250.00,25.000,'Silver',NULL,NULL,NULL),(40,18,'INV-20260919-0010','2026-09-19 22:14:15',5000.00,150.00,0.00,5150.00,'Completed',88,'Hybrid','Cash',2500.00,1000.00,1650.00,0.000,NULL,NULL,NULL,NULL),(41,19,'INV-20260919-0011','2026-09-19 22:18:06',5000.00,150.00,0.00,5150.00,'Completed',88,'Hybrid','Cash',2500.00,1000.00,1650.00,0.000,NULL,NULL,NULL,NULL),(42,18,'INV-20260919-0012','2026-09-19 22:21:24',2500.00,75.00,0.00,2575.00,'Completed',88,'Hybrid','Metal',1250.00,500.00,825.00,3.300,'Silver',NULL,NULL,NULL),(44,18,'INV-20260919-0013','2026-09-19 22:57:47',8000.00,240.00,0.00,8240.00,'Completed',88,'Metal','Metal',4750.00,0.00,3490.00,0.481,'Gold',NULL,NULL,NULL),(45,18,'INV-20260919-0014','2026-09-19 23:11:59',17638.00,529.14,0.00,18167.00,'Completed',88,'Hybrid','Cash',0.00,0.00,18167.00,0.000,NULL,0.000,0.000,NULL),(46,2,'INV-20260919-0015','2026-09-19 23:14:00',7500.00,225.00,0.00,7725.00,'Completed',88,'Metal','Metal',3750.00,2000.00,1975.00,0.000,'Silver',0.000,0.000,NULL),(47,3,'INV-20260919-0016','2026-09-19 23:15:14',8400.00,252.00,0.00,8652.00,'Completed',88,'Metal','Metal',5000.00,1500.00,2152.00,0.000,'Silver',0.000,0.000,NULL),(48,18,'INV-20260919-0017','2026-09-19 23:20:57',1770.00,53.10,0.00,1823.00,'Completed',88,'Metal','Metal',450.00,0.00,1373.00,0.000,'Silver',0.000,0.000,NULL),(49,3,'INV-20260919-0018','2026-09-19 23:30:50',13720.00,411.60,0.00,14132.00,'Completed',88,'Hybrid','Metal',0.00,0.00,14132.00,0.000,NULL,0.000,0.000,NULL),(50,3,'INV-20260919-0019','2026-09-19 23:57:18',5000.00,150.00,0.00,5150.00,'Completed',88,'Metal','Metal',3750.00,400.00,1000.00,0.000,'Silver',0.000,0.000,NULL),(51,19,'INV-20260920-0001','2026-09-20 10:33:46',1170.00,35.10,0.00,1205.00,'Completed',88,'Metal','Metal',270.00,500.00,435.00,0.000,'Silver',0.000,0.000,NULL),(52,18,'INV-20260920-0002','2026-09-20 10:35:30',33205.00,996.15,0.00,34201.00,'Completed',88,'Metal','Metal',7250.00,15000.00,11951.00,0.000,'Gold',0.000,0.000,NULL),(53,2,'INV-20260920-0003','2026-09-20 10:45:38',1770.00,53.10,0.00,1823.00,'Completed',88,'Metal','Metal',450.00,500.00,873.00,0.000,'Silver',0.000,0.000,NULL),(54,3,'INV-20260920-0004','2026-09-20 10:47:48',0.00,0.00,0.00,0.00,'Completed',88,'Metal','Cash',0.00,0.00,0.00,0.000,NULL,0.000,0.000,NULL),(55,3,'INV-20260920-0005','2026-09-20 10:57:23',0.00,0.00,0.00,0.00,'Completed',88,'Metal','Cash',0.00,0.00,0.00,0.000,NULL,0.000,0.000,NULL),(56,3,'INV-20260920-0006','2026-09-20 10:58:19',6160.00,184.80,0.00,6345.00,'Completed',88,'Metal','Metal',3750.00,500.00,2095.00,0.000,'Silver',0.000,0.000,NULL),(57,18,'INV-20260920-0007','2026-09-20 13:39:02',17252.00,517.56,0.00,17770.00,'Completed',88,'Hybrid','Metal',5425.00,5000.00,0.00,0.000,'Gold',0.000,0.000,NULL),(58,18,'INV-20260920-0008','2026-09-20 13:50:05',37040.00,1111.20,0.00,38151.00,'Paid',88,'Metal','Cash',3140.00,35011.00,0.00,0.000,'Gold',0.000,0.000,NULL),(59,19,'INV-20260920-0009','2026-09-20 14:08:08',43340.00,1300.20,0.00,44640.00,'Completed',88,'Hybrid','Metal',19375.00,0.00,1300.00,0.000,NULL,0.000,0.000,NULL),(60,3,'INV-20260921-0001','2026-09-21 09:49:23',73915.00,2217.45,0.00,76132.00,'Completed',88,'Hybrid','Metal',36520.00,5000.00,4137.00,0.000,NULL,0.000,0.000,NULL),(61,3,'INV-20260921-0002','2026-09-21 12:32:34',268565.00,8056.95,0.00,276622.00,'Completed',88,'Hybrid','Metal',0.00,0.00,8057.00,0.000,NULL,0.000,0.000,NULL),(62,18,'INV-20260921-0003','2026-09-21 12:49:34',132940.00,3988.20,0.00,136928.00,'Completed',88,'Metal','Metal',58000.00,0.00,4108.00,0.000,'Gold',10.320,0.000,'8.000g Gold'),(63,2,'INV-20260921-0004','2026-09-21 12:51:22',134110.00,4023.30,0.00,138133.00,'Completed',88,'Hybrid','Metal',87450.00,0.00,4143.00,0.000,NULL,6.320,8.000,'12.000g Gold | 5.000g Silver');
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
  KEY `product_id` (`product_id`),
  KEY `purity_id` (`purity_id`),
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_items`
--

LOCK TABLES `purchase_items` WRITE;
/*!40000 ALTER TABLE `purchase_items` DISABLE KEYS */;
INSERT INTO `purchase_items` VALUES (1,1,'Silver','coin','Scrap',100.000,0.000,100.000,5.00,77.00,82.000,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(2,1,'Silver','Old Silver Deposit','Deposit',80.000,0.000,80.000,100.00,0.00,80.000,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(3,2,'Silver','chain','Scrap',20.000,0.000,20.000,50.00,10.00,12.000,15000.00,180000.00,0.00,0.00,0.00,0.00,0.00,180000.00),(4,2,'Silver','Old Silver Deposit','Deposit',5.000,0.000,5.000,100.00,0.00,5.000,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(5,3,'Gold','d','Scrap',23.000,0.000,23.000,82.00,0.00,18.860,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00),(6,3,'Silver','ee','Scrap',22.000,0.000,22.000,100.00,0.00,22.000,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00);
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
  `bill_type` varchar(50) DEFAULT 'Cash',
  `settlement_type` varchar(50) DEFAULT 'Cash',
  `settlement_metal_type` varchar(50) DEFAULT NULL,
  `metal_given_value` decimal(12,2) DEFAULT '0.00',
  `cash_paid` decimal(12,2) DEFAULT '0.00',
  `balance_amount` decimal(12,2) DEFAULT '0.00',
  `gold_balance_metal_weight` decimal(12,3) DEFAULT '0.000',
  `silver_balance_metal_weight` decimal(12,3) DEFAULT '0.000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_purchases_purchase_number` (`purchase_number`),
  KEY `seller_id` (`seller_id`),
  KEY `created_by_id` (`created_by_id`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`id`),
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (1,'PUR-54370',1,1,'2026-08-10 04:10:54',0.00,0.00,0.00,0.00,0.00,'COMPLETED','Cash','Cash',NULL,0.00,0.00,0.00,0.000,0.000),(2,'PUR-359672',1,1,'2026-08-28 05:02:40',180000.00,0.00,0.00,0.00,180000.00,'COMPLETED','Cash','Cash',NULL,0.00,0.00,0.00,0.000,0.000),(3,'PUR-47451',1,89,'2026-09-20 17:07:27',0.00,0.00,0.00,0.00,0.00,'COMPLETED','Cash','Cash',NULL,0.00,0.00,0.00,0.000,0.000);
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
  KEY `metal_type_id` (`metal_type_id`),
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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Admin','Administrator');
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
  `fine_gold_balance` decimal(10,3) NOT NULL,
  `fine_silver_balance` decimal(10,3) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_sellers_name` (`name`),
  KEY `ix_sellers_mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sellers`
--

LOCK TABLES `sellers` WRITE;
/*!40000 ALTER TABLE `sellers` DISABLE KEYS */;
INSERT INTO `sellers` VALUES (1,'nilu','2222222122',NULL,NULL,'','',0.00,18.860,201.000,1),(2,'nilu','2224445556',NULL,NULL,'pali','',0.00,0.000,0.000,1);
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
  `key` varchar(100) NOT NULL,
  `value` text NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_settings_key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'business_name','SAIDEEP JEWELLERS',NULL),(2,'phone','9460820878',NULL),(3,'gstin','BNUPK1610E1Z3',NULL),(4,'email','saideepjeweller78@gmail.com',NULL);
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
  `applied_rate` decimal(10,2) NOT NULL,
  `gross_weight` decimal(10,3) NOT NULL,
  `tanch_percentage` decimal(5,2) NOT NULL,
  `pure_weight` decimal(10,3) NOT NULL,
  `making_charge_type` varchar(20) NOT NULL,
  `making_charge_rate` decimal(10,2) NOT NULL,
  `making_charges_amount` decimal(10,2) NOT NULL,
  `total_silver_value` decimal(12,2) NOT NULL,
  `wastage` decimal(5,2) NOT NULL,
  `other_charges` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  `stone_weight` decimal(10,3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_item_id` (`invoice_item_id`),
  KEY `metal_rate_id` (`metal_rate_id`),
  CONSTRAINT `silver_calculations_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `silver_calculations_ibfk_2` FOREIGN KEY (`metal_rate_id`) REFERENCES `silver_rates` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `silver_calculations`
--

LOCK TABLES `silver_calculations` WRITE;
/*!40000 ALTER TABLE `silver_calculations` DISABLE KEYS */;
INSERT INTO `silver_calculations` VALUES (1,1,NULL,900.00,45.000,100.00,45.000,'flat',0.00,0.00,40500.00,0.00,0.00,0.00,NULL),(2,6,NULL,0.00,100.000,78.00,83.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(3,7,NULL,0.00,100.000,65.00,70.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(4,9,NULL,0.00,100.000,65.00,70.000,'flat',0.00,3000.00,0.00,0.00,0.00,0.00,NULL),(5,21,NULL,0.00,100.000,65.00,73.000,'flat',0.00,300.00,0.00,8.00,0.00,0.00,NULL),(6,22,NULL,0.00,70.000,100.00,70.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(7,24,NULL,0.00,100.000,65.00,72.000,'flat',0.00,300.00,0.00,7.00,0.00,0.00,NULL),(8,26,NULL,0.00,25.000,100.00,25.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(9,30,NULL,0.00,1000.000,65.00,720.000,'flat',0.00,0.00,0.00,7.00,0.00,0.00,NULL),(10,32,NULL,0.00,700.000,100.00,700.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(11,33,NULL,0.00,100.000,65.00,75.000,'flat',0.00,0.00,0.00,10.00,0.00,0.00,NULL),(12,34,NULL,0.00,50.000,100.00,50.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(13,35,NULL,0.00,10.000,99.90,9.990,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(14,36,NULL,0.00,7.000,100.00,7.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(15,41,NULL,250000.00,100.000,65.00,76.400,'flat',0.00,3000.00,19100000.00,11.40,0.00,0.00,NULL),(16,42,NULL,0.00,15.000,100.00,15.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(17,43,NULL,250000.00,200.000,65.00,170.000,'flat',0.00,0.00,42500000.00,20.00,0.00,0.00,NULL),(18,44,NULL,0.00,50.000,100.00,50.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(19,47,NULL,0.00,100.000,75.00,81.000,'flat',0.00,0.00,0.00,6.00,0.00,0.00,NULL),(20,48,NULL,0.00,50.000,100.00,50.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,NULL),(21,49,NULL,90000.00,100.000,75.00,81.000,'flat',0.00,0.00,7290000.00,6.00,0.00,0.00,NULL),(22,50,NULL,90000.00,20.000,100.00,20.000,'flat',0.00,0.00,1800000.00,0.00,0.00,0.00,NULL),(23,53,NULL,250000.00,20.000,76.00,16.400,'flat',0.00,0.00,4100000.00,6.00,0.00,0.00,NULL),(24,54,NULL,250000.00,2.000,100.00,2.000,'flat',0.00,0.00,500000.00,0.00,0.00,0.00,NULL),(25,55,NULL,250000.00,50.000,100.00,50.000,'flat',0.00,0.00,12500.00,0.00,0.00,0.00,NULL),(26,56,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,NULL),(27,57,NULL,250000.00,50.000,100.00,50.000,'flat',0.00,0.00,12500.00,0.00,0.00,0.00,NULL),(28,58,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,NULL),(29,59,NULL,250000.00,50.000,100.00,50.000,'flat',0.00,0.00,12500.00,0.00,0.00,0.00,NULL),(30,60,NULL,250000.00,25.000,100.00,25.000,'flat',0.00,0.00,6250.00,0.00,0.00,0.00,NULL),(31,61,NULL,250000.00,100.000,100.00,100.000,'flat',0.00,0.00,25000.00,0.00,0.00,0.00,NULL),(32,62,NULL,250000.00,50.000,100.00,50.000,'flat',0.00,0.00,12500.00,0.00,0.00,0.00,NULL),(33,63,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,NULL),(34,64,NULL,250000.00,10.000,100.00,10.000,'flat',0.00,0.00,2500.00,0.00,0.00,0.00,NULL),(35,65,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,NULL),(36,66,NULL,250000.00,10.000,100.00,10.000,'flat',0.00,0.00,2500.00,0.00,0.00,0.00,NULL),(37,67,NULL,250000.00,10.000,100.00,10.000,'flat',0.00,0.00,2500.00,0.00,0.00,0.00,NULL),(38,68,NULL,250000.00,5.000,100.00,5.000,'flat',0.00,0.00,1250.00,0.00,0.00,0.00,NULL),(39,73,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,0.000),(40,75,NULL,250000.00,10.000,100.00,10.000,'flat',0.00,0.00,2500.00,0.00,0.00,0.00,0.000),(41,77,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,600.00,1170.00,0.00,0.00,0.00,0.000),(42,78,NULL,250000.00,30.000,100.00,30.000,'flat',0.00,0.00,7500.00,0.00,0.00,0.00,0.000),(43,79,NULL,250000.00,15.000,100.00,15.000,'flat',0.00,0.00,3750.00,0.00,0.00,0.00,0.000),(44,80,NULL,250000.00,30.000,100.00,30.000,'flat',0.00,900.00,7500.00,0.00,0.00,0.00,0.000),(45,81,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,0.000),(46,82,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,600.00,1170.00,0.00,0.00,0.00,0.000),(47,83,NULL,90000.00,5.000,100.00,5.000,'flat',0.00,0.00,450.00,0.00,0.00,0.00,0.000),(48,85,NULL,0.00,20.000,65.00,13.000,'flat',0.00,600.00,0.00,0.00,0.00,0.00,0.000),(49,87,NULL,0.00,4.000,100.00,4.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000),(50,88,NULL,250000.00,20.000,100.00,20.000,'flat',0.00,0.00,5000.00,0.00,0.00,0.00,0.000),(51,89,NULL,250000.00,15.000,100.00,15.000,'flat',0.00,0.00,3750.00,0.00,0.00,0.00,0.000),(52,90,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,0.00,1170.00,0.00,0.00,0.00,0.000),(53,91,NULL,90000.00,3.000,100.00,3.000,'flat',0.00,0.00,270.00,0.00,0.00,0.00,0.000),(54,94,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,600.00,1170.00,0.00,0.00,0.00,0.000),(55,95,NULL,90000.00,5.000,100.00,5.000,'flat',0.00,0.00,450.00,0.00,0.00,0.00,0.000),(56,96,NULL,0.00,20.000,85.00,17.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000),(57,97,NULL,0.00,5.000,100.00,5.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000),(58,98,NULL,0.00,32.000,65.00,20.800,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000),(59,99,NULL,0.00,15.000,100.00,15.000,'flat',0.00,0.00,0.00,0.00,0.00,0.00,0.000),(60,100,NULL,250000.00,32.000,65.00,24.640,'flat',0.00,0.00,6160.00,12.00,0.00,0.00,0.000),(61,101,NULL,250000.00,15.000,100.00,15.000,'flat',0.00,0.00,3750.00,0.00,0.00,0.00,0.000),(62,103,NULL,90000.00,50.000,65.00,42.500,'flat',0.00,0.00,3825.00,20.00,0.00,0.00,0.000),(63,105,NULL,90000.00,20.000,100.00,20.000,'flat',0.00,0.00,1800.00,0.00,0.00,0.00,0.000),(64,108,NULL,90000.00,100.000,65.00,70.000,'flat',0.00,0.00,6300.00,5.00,0.00,0.00,0.000),(65,111,NULL,90000.00,50.000,75.00,37.500,'flat',0.00,0.00,3375.00,0.00,0.00,0.00,0.000),(66,113,NULL,90000.00,10.000,65.00,6.500,'flat',0.00,300.00,585.00,0.00,0.00,0.00,0.000),(67,115,NULL,90000.00,3.000,100.00,3.000,'flat',0.00,0.00,270.00,0.00,0.00,0.00,0.000),(68,117,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,0.00,1170.00,0.00,0.00,0.00,0.000),(69,118,NULL,90000.00,30.000,65.00,19.500,'flat',0.00,0.00,1755.00,0.00,0.00,0.00,0.000),(70,123,NULL,90000.00,20.000,65.00,13.000,'flat',0.00,0.00,1170.00,0.00,0.00,0.00,0.000),(71,125,NULL,90000.00,5.000,100.00,5.000,'flat',0.00,0.00,450.00,0.00,0.00,0.00,0.000);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `rate_per_gram` decimal(10,2) NOT NULL,
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
  `wastage` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_stock_items_item_code` (`item_code`),
  KEY `ix_stock_items_metal` (`metal`),
  KEY `ix_stock_items_category` (`category`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_items`
--

LOCK TABLES `stock_items` WRITE;
/*!40000 ALTER TABLE `stock_items` DISABLE KEYS */;
INSERT INTO `stock_items` VALUES (1,'SLV-000001','1','Silver','chain','','22K916',45.00,45.000,0.000,45.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000001.png','','Sold','2026-08-06 05:24:42','2026-08-06 05:26:01',NULL),(2,'GLD-000001','coin','Gold','','','22K916',77.00,100.000,0.000,100.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/GLD-000001.png','','Sold','2026-08-06 12:45:34','2026-08-10 04:08:01',NULL),(3,'GLD-000002','coin','Gold','','','22K916',91.60,20.000,0.000,20.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/GLD-000002.png','','Sold','2026-08-28 04:57:03','2026-08-28 15:09:54',NULL),(4,'SLV-000002','payall','Silver','jodhupuri ','','22K916',75.00,100.000,0.000,100.000,'flat',0.00,0.00,0.00,'','',NULL,'/static/qrcodes/SLV-000002.png','','Sold','2026-09-19 13:01:41','2026-09-19 15:33:50',6.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_ledgers`
--

LOCK TABLES `supplier_ledgers` WRITE;
/*!40000 ALTER TABLE `supplier_ledgers` DISABLE KEYS */;
INSERT INTO `supplier_ledgers` VALUES (1,1,'2026-08-10 04:10:54','Purchase','PUR-54370','Purchase PUR-54370',0.00,0.00,0.00,0.000,0.000,0.000,0.000,162.000,162.000),(2,1,'2026-08-28 05:02:40','Purchase','PUR-359672','Purchase PUR-359672',0.00,180000.00,180000.00,0.000,0.000,0.000,0.000,17.000,179.000),(3,1,'2026-08-28 05:02:40','Payment','PAY-PUR-359672','Payment for Purchase PUR-359672',80000.00,0.00,100000.00,0.000,0.000,0.000,0.000,0.000,179.000),(4,1,'2026-09-20 17:07:28','Purchase','PUR-47451','Purchase PUR-47451',0.00,0.00,0.00,0.000,18.860,18.860,0.000,22.000,201.000);
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
  `is_deleted` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_suppliers_mobile` (`mobile`),
  KEY `ix_suppliers_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@example.com','$2b$12$E2nd11SzPkhJAki9LrsBTuMXHZxixXuQ0ggi7cZhNxX1WLTBCP24q','System Admin',1,1,'2026-08-06 09:45:27',NULL),(88,'yashsony23478@gmail.com','yashsony23478@gmail.com','$2b$12$9VslxzIwXaQ65W5XplHipeLKoEEv0Mzcqg9aVlaavxwipZul4FeBm','Yash Soni',1,1,'2026-09-19 18:23:49',NULL),(89,'yashsoni23478@gmail.com','yashsoni23478@gmail.com','$2b$12$agVlcjFWUjwd7dZ1Jf2EKu0NU2NaOqkvWimjNg6.6P89OnO1CeGz6','YASH SONI',1,1,'2026-09-20 18:15:22',NULL);
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

-- Dump completed on 2026-09-21 18:53:55
