-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: gymdb
-- ------------------------------------------------------
<<<<<<< HEAD
-- Server version	9.3.0
=======
-- Server version	8.0.42
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `coach`
--

DROP TABLE IF EXISTS `coach`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coach` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `coach_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coach`
--

LOCK TABLES `coach` WRITE;
/*!40000 ALTER TABLE `coach` DISABLE KEYS */;
<<<<<<< HEAD
INSERT INTO `coach` VALUES (2),(5),(10),(11),(12),(13),(14);
=======
INSERT INTO `coach` VALUES (2),(5),(10),(11),(12),(13),(14),(20);
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `coach` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exercise`
--

DROP TABLE IF EXISTS `exercise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise` (
  `description` varchar(100) NOT NULL,
  `image` varchar(150) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exercise`
--

LOCK TABLES `exercise` WRITE;
/*!40000 ALTER TABLE `exercise` DISABLE KEYS */;
INSERT INTO `exercise` VALUES ('vào lưng, tăng sức bền','https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172002_mjx9mg.png',1,'Pull up'),('vào ngực giữa, tăng sức bền','https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172013_x4kl3z.png',2,'Dumbbel Press'),('vào ngực giữa, tăng sức bền','https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-12-06_101255_flozvt.png',3,'Bar bell'),('vào ngực dưới vai, tăng sức bền','https://res.cloudinary.com/dpl8syyb9/image/upload/v1764992819/Screenshot_2025-12-06_104738_c2u0nw.png',4,'Dip');
/*!40000 ALTER TABLE `exercise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exercise_schedule`
--

DROP TABLE IF EXISTS `exercise_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise_schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_detail_id` int NOT NULL,
  `day` enum('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `plan_detail_id` (`plan_detail_id`),
  CONSTRAINT `exercise_schedule_ibfk_1` FOREIGN KEY (`plan_detail_id`) REFERENCES `plan_detail` (`id`)
<<<<<<< HEAD
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
=======
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exercise_schedule`
--

LOCK TABLES `exercise_schedule` WRITE;
/*!40000 ALTER TABLE `exercise_schedule` DISABLE KEYS */;
<<<<<<< HEAD
=======
INSERT INTO `exercise_schedule` VALUES (1,1,'MONDAY'),(2,1,'TUESDAY'),(3,1,'THURSDAY'),(4,2,'TUESDAY'),(5,2,'WEDNESDAY'),(6,2,'THURSDAY'),(7,3,'TUESDAY'),(8,3,'WEDNESDAY'),(9,3,'FRIDAY'),(10,4,'MONDAY'),(11,4,'TUESDAY'),(12,4,'WEDNESDAY'),(13,4,'THURSDAY'),(14,5,'MONDAY'),(15,5,'TUESDAY'),(16,5,'WEDNESDAY'),(17,6,'MONDAY'),(18,6,'TUESDAY'),(19,6,'WEDNESDAY'),(20,7,'MONDAY'),(21,7,'TUESDAY'),(22,7,'THURSDAY'),(23,8,'THURSDAY'),(24,8,'FRIDAY'),(25,9,'MONDAY'),(26,9,'TUESDAY'),(27,9,'WEDNESDAY'),(28,9,'THURSDAY'),(29,9,'FRIDAY'),(30,10,'MONDAY'),(31,10,'TUESDAY'),(32,10,'WEDNESDAY'),(33,10,'THURSDAY'),(34,10,'FRIDAY'),(35,10,'SATURDAY'),(36,11,'MONDAY'),(37,11,'TUESDAY'),(38,11,'WEDNESDAY'),(39,11,'THURSDAY'),(40,11,'FRIDAY'),(41,11,'SATURDAY'),(42,12,'MONDAY'),(43,12,'TUESDAY'),(44,12,'WEDNESDAY'),(45,12,'THURSDAY'),(46,12,'FRIDAY'),(47,13,'THURSDAY'),(48,13,'FRIDAY'),(49,13,'SATURDAY'),(50,13,'SUNDAY'),(51,14,'MONDAY'),(52,14,'TUESDAY'),(53,14,'WEDNESDAY'),(54,14,'THURSDAY'),(55,14,'FRIDAY');
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `exercise_schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice`
--

DROP TABLE IF EXISTS `invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `status` enum('PENDING','PAID','FAILED') DEFAULT NULL,
  `total_amount` double NOT NULL,
  `payment_date` datetime DEFAULT NULL,
<<<<<<< HEAD
  `invoice_day_create` datetime DEFAULT NULL,
=======
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
  PRIMARY KEY (`id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
<<<<<<< HEAD
INSERT INTO `invoice` VALUES (1,6,'PENDING',500000,'2025-12-12 16:46:30','2025-12-12 16:30:00'),(2,6,'PAID',500000,'2025-12-12 16:48:13','2025-12-12 16:40:15'),(3,4,'PENDING',1500000,'2025-12-12 18:15:14','2025-12-12 10:15:00'),(4,4,'PAID',1500000,'2025-12-12 18:15:36','2025-12-12 18:00:00'),(5,15,'PENDING',1500000,'2025-12-12 20:05:46','2025-12-11 09:30:00'),(6,16,'PENDING',5000000,'2025-12-12 20:05:53','2025-12-12 19:45:00'),(7,18,'PENDING',300000,'2025-12-12 20:06:09','2025-12-12 20:00:00'),(8,15,'PAID',1500000,'2025-12-12 20:06:39','2025-12-10 14:20:00'),(9,16,'PAID',5000000,'2025-12-12 20:06:48','2025-12-12 15:00:00'),(10,18,'PAID',300000,'2025-12-12 20:06:58','2025-12-12 20:01:00'),(11,17,'PAID',300000,'2025-12-12 20:07:04','2025-12-12 20:05:00');/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;
=======
INSERT INTO `invoice` VALUES (1,6,'PENDING',500000,'2025-12-12 16:46:30'),(2,6,'PAID',500000,'2025-12-12 16:48:13'),(3,4,'PENDING',1500000,'2025-12-12 18:15:14'),(4,4,'PAID',1500000,'2025-12-12 18:15:36'),(5,15,'PENDING',1500000,'2025-12-12 20:05:46'),(6,16,'PENDING',5000000,'2025-12-12 20:05:53'),(7,18,'PENDING',300000,'2025-12-12 20:06:09'),(8,15,'PAID',1500000,'2025-12-12 20:06:39'),(9,16,'PAID',5000000,'2025-12-12 20:06:48'),(10,18,'PAID',300000,'2025-12-12 20:06:58'),(11,17,'PAID',300000,'2025-12-12 20:07:04');
/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
UNLOCK TABLES;

--
-- Table structure for table `invoice_detail`
--

DROP TABLE IF EXISTS `invoice_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `amount` double NOT NULL,
  `member_package_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `member_package_id` (`member_package_id`),
  CONSTRAINT `invoice_detail_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoice` (`id`),
  CONSTRAINT `invoice_detail_ibfk_2` FOREIGN KEY (`member_package_id`) REFERENCES `member_package` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_detail`
--

LOCK TABLES `invoice_detail` WRITE;
/*!40000 ALTER TABLE `invoice_detail` DISABLE KEYS */;
INSERT INTO `invoice_detail` VALUES (1,2,500000,3),(2,4,1500000,5),(3,8,1500000,9),(4,9,5000000,10),(5,10,300000,11),(6,11,300000,12);
/*!40000 ALTER TABLE `invoice_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `member_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
INSERT INTO `member` VALUES (4),(6),(7),(9),(15),(16),(17),(18);
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member_package`
--

DROP TABLE IF EXISTS `member_package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_package` (
  `id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `package_id` int NOT NULL,
<<<<<<< HEAD
  `startDate` datetime DEFAULT NULL,
  `endDate` datetime DEFAULT NULL,
=======
  `startDate` datetime NOT NULL,
  `endDate` datetime NOT NULL,
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
  `status` enum('ACTIVE','EXPIRED') DEFAULT NULL,
  `coach_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `member_id` (`member_id`),
  KEY `package_id` (`package_id`),
  KEY `coach_id` (`coach_id`),
  CONSTRAINT `member_package_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`),
  CONSTRAINT `member_package_ibfk_2` FOREIGN KEY (`package_id`) REFERENCES `package` (`id`),
  CONSTRAINT `member_package_ibfk_3` FOREIGN KEY (`coach_id`) REFERENCES `coach` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_package`
--

LOCK TABLES `member_package` WRITE;
/*!40000 ALTER TABLE `member_package` DISABLE KEYS */;
<<<<<<< HEAD
INSERT INTO `member_package` VALUES (1,7,1,'2025-12-09 20:22:48','2026-01-08 20:22:48','ACTIVE',2),(3,6,2,'2025-12-12 16:48:13','2026-01-11 16:48:13','ACTIVE',10),(5,4,3,'2025-12-12 18:15:36','2026-01-11 18:15:36','ACTIVE',12),(6,15,3,'2025-12-12 20:05:46','2026-01-12 20:05:46','EXPIRED',NULL),(7,16,4,'2025-12-12 20:05:53','2026-01-12 20:05:53','EXPIRED',NULL),(8,18,1,'2025-12-12 20:06:09','2026-01-12 20:06:09','EXPIRED',NULL),(9,15,3,'2025-12-12 20:06:39','2026-01-11 20:06:39','ACTIVE',13),(10,16,4,'2025-12-12 20:06:48','2026-01-11 20:06:48','ACTIVE',5),(11,18,1,'2025-12-12 20:06:58','2026-01-11 20:06:58','ACTIVE',10),(12,17,1,'2025-12-12 20:07:04','2026-01-11 20:07:04','ACTIVE',NULL);
=======
INSERT INTO `member_package` VALUES (1,7,1,'2025-12-09 20:22:48','2026-01-08 20:22:48','ACTIVE',11),(3,6,2,'2025-12-12 16:48:13','2026-01-11 16:48:13','ACTIVE',5),(5,4,3,'2025-12-12 18:15:36','2026-01-11 18:15:36','ACTIVE',12),(6,15,3,'2025-12-12 20:05:46','2026-01-12 20:05:46','EXPIRED',NULL),(7,16,4,'2025-12-12 20:05:53','2026-01-12 20:05:53','EXPIRED',NULL),(8,18,1,'2025-12-12 20:06:09','2026-01-12 20:06:09','EXPIRED',NULL),(9,15,3,'2025-12-12 20:06:39','2026-01-11 20:06:39','ACTIVE',13),(10,16,4,'2025-12-12 20:06:48','2026-01-11 20:06:48','ACTIVE',5),(11,18,1,'2025-12-12 20:06:58','2026-01-11 20:06:58','ACTIVE',5),(12,17,1,'2025-12-12 20:07:04','2026-01-11 20:07:04','ACTIVE',12);
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `member_package` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `package`
--

DROP TABLE IF EXISTS `package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package` (
  `duration` int NOT NULL,
  `price` double NOT NULL,
  `description` text NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package`
--

LOCK TABLES `package` WRITE;
/*!40000 ALTER TABLE `package` DISABLE KEYS */;
INSERT INTO `package` VALUES (1,300000,'Gói cơ bản với đầy đủ thiết bị và tiện ích cần thiết cho người mới bắt đầu.','https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png',1,'CLASSIC'),(1,500000,'Nâng cấp từ CLASSIC, thêm quyền truy cập 24/7 và các dịch vụ phục hồi.','https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157774/bac_ljtnva.png',2,'CLASSIC-PLUS'),(1,1500000,'Gói cao cấp với PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.','https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vang_igx7ax.png',3,'ROYRAL'),(1,5000000,'Gói VIP với tất cả quyền lợi ROYRAL, PT riêng nhiều buổi và ưu tiên dịch vụ tối đa.','https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vip_xsz4c4.png',4,'SIGNATURE');
/*!40000 ALTER TABLE `package` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `package_benefit`
--

DROP TABLE IF EXISTS `package_benefit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package_benefit` (
  `detail` text,
  `package_id` int NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `package_id` (`package_id`),
  CONSTRAINT `package_benefit_ibfk_1` FOREIGN KEY (`package_id`) REFERENCES `package` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package_benefit`
--

LOCK TABLES `package_benefit` WRITE;
/*!40000 ALTER TABLE `package_benefit` DISABLE KEYS */;
INSERT INTO `package_benefit` VALUES ('Truy cập phòng tập từ 6:00 - 22:00 hằng ngày',1,1,'Truy cập phòng tập'),('Toàn bộ máy móc và khu vực tập luyện trong phòng gym',1,2,'Sử dụng tất cả thiết bị'),('Tiện nghi cơ bản cho thành viên sau khi tập luyện',1,3,'Phòng thay đồ & tắm'),('Kết nối internet tốc độ cao trong toàn khu vực phòng tập',1,4,'Wi-Fi không giới hạn'),('Cung cấp nước uống cơ bản trong mỗi buổi tập',1,5,'Nước uống miễn phí'),('Tập luyện bất cứ thời điểm nào trong ngày',2,6,'Truy cập 24/7'),('Bao gồm toàn bộ ưu đãi trong gói CLASSIC',2,7,'Tất cả quyền lợi của CLASSIC'),('Thư giãn và phục hồi thể lực sau buổi tập',2,8,'Phòng sauna & phục hồi'),('Một buổi huấn luyện viên cá nhân mỗi tháng',2,9,'1 buổi PT/tháng miễn phí'),('Không giới hạn thời gian sử dụng phòng tập',3,10,'Truy cập 24/7'),('Huấn luyện viên cá nhân theo sát mục tiêu tập luyện',3,11,'4 buổi PT cá nhân/tháng'),('Xây dựng chế độ ăn phù hợp với thể trạng và mục tiêu',3,12,'Tư vấn dinh dưỡng'),('Đo inbody và đánh giá kết quả luyện tập thường xuyên',3,13,'Kiểm tra thân hình định kỳ'),('Không gian thư giãn riêng sau khi tập luyện',3,14,'Phòng thư giãn cao cấp'),('Dễ dàng chọn giờ đẹp với huấn luyện viên yêu thích',3,15,'Ưu tiên đặt lịch PT'),('Bao gồm truy cập 24/7, PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.',4,16,'Tất cả quyền lợi gói ROYRAL'),('Lịch tập 1–1 với huấn luyện viên cá nhân, trung bình 2 buổi/tuần (tối đa 8 buổi/tháng).',4,17,'8 buổi PT cá nhân/tháng'),('Một huấn luyện viên theo sát, xây dựng giáo trình và điều chỉnh bài tập riêng cho bạn.',4,18,'Huấn luyện viên riêng'),('Đo chỉ số cơ thể (như InBody) định kỳ 2 tuần/lần để theo dõi tiến độ và tối ưu giáo án.',4,19,'Phân tích cơ thể mỗi 2 tuần'),('Ưu tiên đặt lịch sử dụng máy tập, phòng chức năng và các dịch vụ cao cấp trong giờ cao điểm.',4,20,'Ưu tiên máy & phòng tập');
/*!40000 ALTER TABLE `package_benefit` ENABLE KEYS */;
UNLOCK TABLES;

--
<<<<<<< HEAD
-- Table structure for table `package_plan_assignment`
--

DROP TABLE IF EXISTS `package_plan_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package_plan_assignment` (
  `workout_plan_id` int NOT NULL,
  `member_package_id` int NOT NULL,
  KEY `workout_plan_id` (`workout_plan_id`),
  KEY `member_package_id` (`member_package_id`),
  CONSTRAINT `package_plan_assignment_ibfk_1` FOREIGN KEY (`workout_plan_id`) REFERENCES `workout_plan` (`id`),
  CONSTRAINT `package_plan_assignment_ibfk_2` FOREIGN KEY (`member_package_id`) REFERENCES `member_package` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package_plan_assignment`
--

LOCK TABLES `package_plan_assignment` WRITE;
/*!40000 ALTER TABLE `package_plan_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `package_plan_assignment` ENABLE KEYS */;
=======
-- Table structure for table `plan_assignment`
--

DROP TABLE IF EXISTS `plan_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan_assignment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `workout_plan_id` int NOT NULL,
  `member_package_id` int NOT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `workout_plan_id` (`workout_plan_id`),
  KEY `member_package_id` (`member_package_id`),
  CONSTRAINT `plan_assignment_ibfk_1` FOREIGN KEY (`workout_plan_id`) REFERENCES `workout_plan` (`id`),
  CONSTRAINT `plan_assignment_ibfk_2` FOREIGN KEY (`member_package_id`) REFERENCES `member_package` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan_assignment`
--

LOCK TABLES `plan_assignment` WRITE;
/*!40000 ALTER TABLE `plan_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `plan_assignment` ENABLE KEYS */;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
UNLOCK TABLES;

--
-- Table structure for table `plan_detail`
--

DROP TABLE IF EXISTS `plan_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `workout_plan_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  `reps` int NOT NULL,
  `sets` int NOT NULL,
  `note` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `workout_plan_id` (`workout_plan_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `plan_detail_ibfk_1` FOREIGN KEY (`workout_plan_id`) REFERENCES `workout_plan` (`id`),
  CONSTRAINT `plan_detail_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`id`)
<<<<<<< HEAD
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
=======
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan_detail`
--

LOCK TABLES `plan_detail` WRITE;
/*!40000 ALTER TABLE `plan_detail` DISABLE KEYS */;
<<<<<<< HEAD
=======
INSERT INTO `plan_detail` VALUES (1,1,1,1,2,NULL),(2,1,2,1,3,NULL),(3,1,3,1,3,NULL),(4,1,4,2,3,NULL),(5,2,1,1,1,NULL),(6,3,2,1,2,NULL),(7,3,3,1,1,NULL),(8,8,2,2,3,NULL),(9,8,3,1,5,NULL),(10,13,3,4,3,NULL),(11,14,1,4,4,NULL),(12,14,2,4,4,NULL),(13,14,3,3,4,NULL),(14,14,4,5,4,NULL);
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `plan_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regulation`
--

DROP TABLE IF EXISTS `regulation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regulation` (
  `code` varchar(100) NOT NULL,
  `value` varchar(100) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regulation`
--

LOCK TABLES `regulation` WRITE;
/*!40000 ALTER TABLE `regulation` DISABLE KEYS */;
/*!40000 ALTER TABLE `regulation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `avatar` varchar(150) DEFAULT NULL,
<<<<<<< HEAD
  `email` varchar(100) DEFAULT NULL,
=======
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `user_role` enum('ADMIN','USER','COACH','RECEPTIONIST','CASHIER') DEFAULT NULL,
  `join_date` datetime DEFAULT NULL,
  `dob` datetime DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `gender` enum('MALE','FEMALE') DEFAULT NULL,
  `type` varchar(50) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
<<<<<<< HEAD
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
=======
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
<<<<<<< HEAD
INSERT INTO `user` VALUES ('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg',NULL,'admin','e10adc3949ba59abbe56e057f20f883e','ADMIN','2025-12-09 20:22:48',NULL,NULL,'MALE','user',1,'admin'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540197/Screenshot_2025-12-12_185052_mlep1o.png',NULL,'dangbeo','d9b1d7db4cd6e70935368a1efb10e377','COACH','2025-12-09 20:22:48',NULL,NULL,'MALE','trainer',2,'đăng béo'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg',NULL,'canh','e10adc3949ba59abbe56e057f20f883e','CASHIER','2025-12-09 20:22:48',NULL,NULL,'MALE','user',3,'canh huynh'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg',NULL,'cozg','e10adc3949ba59abbe56e057f20f883e','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',4,'cozgdeptrai'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765199333/Screenshot_2025-12-08_200923_qqbckv.png',NULL,'hoigym','202cb962ac59075b964b07152d234b70','COACH','2025-12-09 20:22:48',NULL,NULL,'MALE','trainer',5,'hợi gym'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765200160/xb2vpquxw3gv0mxi7bbk.png',NULL,'ronaldo','202cb962ac59075b964b07152d234b70','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',6,'ronaldo'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1762914467/xby2eoj58t4dsi3u6vdj.jpg',NULL,'messi','202cb962ac59075b964b07152d234b70','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',7,'messi'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1762590455/cld-sample-5.jpg',NULL,'letan','202cb962ac59075b964b07152d234b70','RECEPTIONIST','2025-12-11 21:39:09','2025-12-11 21:39:00',NULL,'MALE','user',8,'nem chua'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png',NULL,'neymar','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:18:25','0202-12-12 19:29:53','0969293472','MALE','member',9,'neymar'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765539914/Screenshot_2025-12-12_184516_hina0j.png',NULL,'chinh','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:46:43','2025-12-12 18:46:00','0969293472','MALE','trainer',10,'Lê trung chính'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540070/Screenshot_2025-12-12_184839_nmbf5x.png',NULL,'vu','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:49:31','2025-12-12 18:46:00','0969293472','MALE','trainer',11,'Ông Zũ'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540237/download_t05ied.jpg',NULL,'cong','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:52:02','2025-12-12 18:46:00','123','MALE','trainer',12,'công ngu'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540360/Screenshot_2025-12-12_185333_bitxsc.png',NULL,'nhan','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:54:06','2025-12-12 18:46:00','0969293472','MALE','trainer',13,'Phạm Kim Nhân'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540438/Screenshot_2025-12-12_185440_ipyvbt.png',NULL,'sam','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:55:10','2025-12-12 18:46:00','0969293472','MALE','trainer',14,'Sam Sulek'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544550/Screenshot_2025-12-12_200213_vbe930.png',NULL,'robben','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:03:48',NULL,'123','MALE','member',15,'robben'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544551/Screenshot_2025-12-12_200232_lbgvm5.png',NULL,'muller','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:07',NULL,'123','MALE','member',16,'muller'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544550/Screenshot_2025-12-12_200315_dk8jxw.png',NULL,'vinicius','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:27',NULL,'123','MALE','member',17,'vinicius'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544551/Screenshot_2025-12-12_200309_nhpp3c.png',NULL,'antony','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:48',NULL,'0969293472','MALE','member',18,'Antony De Santos');
=======
INSERT INTO `user` VALUES ('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg','admin','e10adc3949ba59abbe56e057f20f883e','ADMIN','2025-12-09 20:22:48',NULL,NULL,'MALE','user',1,'admin'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540197/Screenshot_2025-12-12_185052_mlep1o.png','dangbeo','d9b1d7db4cd6e70935368a1efb10e377','COACH','2025-12-09 20:22:48',NULL,NULL,'MALE','trainer',2,'đăng béo'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg','canh','e10adc3949ba59abbe56e057f20f883e','CASHIER','2025-12-09 20:22:48',NULL,NULL,'MALE','user',3,'canh huynh'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg','cozg','e10adc3949ba59abbe56e057f20f883e','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',4,'cozgdeptrai'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765199333/Screenshot_2025-12-08_200923_qqbckv.png','hoigym','202cb962ac59075b964b07152d234b70','COACH','2025-12-09 20:22:48',NULL,NULL,'MALE','trainer',5,'hợi gym'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765200160/xb2vpquxw3gv0mxi7bbk.png','ronaldo','202cb962ac59075b964b07152d234b70','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',6,'ronaldo'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1762914467/xby2eoj58t4dsi3u6vdj.jpg','messi','202cb962ac59075b964b07152d234b70','USER','2025-12-09 20:22:48',NULL,NULL,'MALE','member',7,'messi'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1762590455/cld-sample-5.jpg','letan','202cb962ac59075b964b07152d234b70','RECEPTIONIST','2025-12-11 21:39:09','2025-12-11 21:39:00',NULL,'MALE','user',8,'nem chua'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png','neymar','202cb962ac59075b964b07152d234b70','USER','2025-12-12 18:18:25','0202-12-12 19:29:53','0969293472','MALE','member',9,'neymar'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765539914/Screenshot_2025-12-12_184516_hina0j.png','chinh','202cb962ac59075b964b07152d234b70','COACH','2025-12-12 18:46:43','2025-12-12 18:46:00','0969293472','MALE','trainer',10,'Lê trung chính'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540070/Screenshot_2025-12-12_184839_nmbf5x.png','vu','202cb962ac59075b964b07152d234b70','COACH','2025-12-12 18:49:31','2025-12-12 18:46:00','0969293472','MALE','trainer',11,'Ông Zũ'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540237/download_t05ied.jpg','cong','202cb962ac59075b964b07152d234b70','COACH','2025-12-12 18:52:02','2025-12-12 18:46:00','123','MALE','trainer',12,'công ngu'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540360/Screenshot_2025-12-12_185333_bitxsc.png','nhan','202cb962ac59075b964b07152d234b70','COACH','2025-12-12 18:54:06','2025-12-12 18:46:00','0969293472','MALE','trainer',13,'Phạm Kim Nhân'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765540438/Screenshot_2025-12-12_185440_ipyvbt.png','sam','202cb962ac59075b964b07152d234b70','COACH','2025-12-12 18:55:10','2025-12-12 18:46:00','0969293472','MALE','trainer',14,'Sam Sulek'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544550/Screenshot_2025-12-12_200213_vbe930.png','robben','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:03:48',NULL,'123','MALE','member',15,'robben'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544551/Screenshot_2025-12-12_200232_lbgvm5.png','muller','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:07',NULL,'123','MALE','member',16,'muller'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544550/Screenshot_2025-12-12_200315_dk8jxw.png','vinicius','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:27',NULL,'123','MALE','member',17,'vinicius'),('https://res.cloudinary.com/dpl8syyb9/image/upload/v1765544551/Screenshot_2025-12-12_200309_nhpp3c.png','antony','202cb962ac59075b964b07152d234b70','USER','2025-12-12 20:04:48',NULL,'0969293472','MALE','member',18,'Antony De Santos'),(NULL,'haiem','202cb962ac59075b964b07152d234b70','COACH','2025-12-21 11:05:04','2025-12-21 11:05:00','06465','MALE','trainer',20,'haiem');
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workout_plan`
--

DROP TABLE IF EXISTS `workout_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout_plan` (
  `coach_id` int NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `coach_id` (`coach_id`),
  CONSTRAINT `workout_plan_ibfk_1` FOREIGN KEY (`coach_id`) REFERENCES `coach` (`id`)
<<<<<<< HEAD
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
=======
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workout_plan`
--

LOCK TABLES `workout_plan` WRITE;
/*!40000 ALTER TABLE `workout_plan` DISABLE KEYS */;
<<<<<<< HEAD
=======
INSERT INTO `workout_plan` VALUES (5,1,'tăng cân'),(5,2,'tăng chiều cao'),(5,3,'dadas'),(5,8,'ouukuh'),(5,13,'igiyg'),(5,14,'tăng cân');
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
/*!40000 ALTER TABLE `workout_plan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

<<<<<<< HEAD
-- Dump completed on 2025-12-16 19:43:45
=======
-- Dump completed on 2025-12-21 11:25:24
>>>>>>> a87186dacffd9c87d4b01ef59446715d33588d02
