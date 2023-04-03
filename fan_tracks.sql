-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: fan_tracks
-- ------------------------------------------------------
-- Server version	8.0.31

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
-- Current Database: `fan_tracks`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `fan_tracks` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `fan_tracks`;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `spotifyLink` varchar(100) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `comment` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES ('15P97BTD10YJtrp8ALoTyC','niamh67','fff'),('15P97BTD10YJtrp8ALoTyC','niamh67','zzzzzzzzzz'),('15P97BTD10YJtrp8ALoTyC','sueredmo','whats my name'),('15P97BTD10YJtrp8ALoTyC','sueredmo','dddddddddd'),('15P97BTD10YJtrp8ALoTyC','sueredmo','ddddddddddddd'),('1NbySmTboOlpRTcQTDjWmF','coolguy','This is great :D'),('0pGZVx5u2xmVnpWWPV6AUr','sueredmo','love it !!!!!'),('0pGZVx5u2xmVnpWWPV6AUr','hannah555','this is kind of bad sorry'),('0pGZVx5u2xmVnpWWPV6AUr','nini5','wow this is great! i loveit'),('0pGZVx5u2xmVnpWWPV6AUr','user2','its great actually dont worry'),('3HboadEB7OvIqWofafFA8G','user2','hope you guys like this i worked very hard'),('3HboadEB7OvIqWofafFA8G','user1','its great !!!'),('0pGZVx5u2xmVnpWWPV6AUr','user1','i loooooove this'),('349PxwPI5Y1NeiErzAxt4T','user2','this is great'),('0pGZVx5u2xmVnpWWPV6AUr','user','wow!'),('738SepQC1rDUgIdggnyL6Y','user','hope you like it'),('738SepQC1rDUgIdggnyL6Y','user2','yeah its good');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `friends`
--

DROP TABLE IF EXISTS `friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `friends` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `spotifyId` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `friends`
--

LOCK TABLES `friends` WRITE;
/*!40000 ALTER TABLE `friends` DISABLE KEYS */;
INSERT INTO `friends` VALUES (106,'annaredmo@gmail.ie','annared','123','2023-03-25 19:58:39','x096nnnkjjz2csivy3ypnxj0n'),(107,'niamh@email.com','niamh67','123','2023-03-25 20:01:47','x096nnnkjjz2csivy3ypnxj0n'),(108,'nini@gmail.ie','nini5','123','2023-03-25 20:03:14','x096nnnkjjz2csivy3ypnxj0n'),(109,'hannah@kmail.ie','hannah555','123','2023-03-25 20:05:10','x096nnnkjjz2csivy3ypnxj0n'),(110,'theresa@email.com','coolguy','123','2023-03-25 20:08:10','x096nnnkjjz2csivy3ypnxj0n'),(111,'tresska@umail.com','tresska','123','2023-03-25 20:10:34','x096nnnkjjz2csivy3ypnxj0n'),(112,'robyn@yahoo.ie','robyn5','123','2023-03-25 20:12:13','x096nnnkjjz2csivy3ypnxj0n'),(115,'sueredmo@aaa.com','sueredmo','123','2023-04-02 09:45:51','x096nnnkjjz2csivy3ypnxj0n'),(117,'user6@gmail.com','user2','12345','2023-04-03 09:13:13','x096nnnkjjz2csivy3ypnxj0n'),(118,'user1@email.com','user1','123','2023-04-03 09:21:58','x096nnnkjjz2csivy3ypnxj0n'),(119,'user@email.com','user','123','2023-04-03 09:27:39','x096nnnkjjz2csivy3ypnxj0n');
/*!40000 ALTER TABLE `friends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `playlist`
--

DROP TABLE IF EXISTS `playlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `playlist` (
  `userid` varchar(100) DEFAULT NULL,
  `playlisttitle` varchar(100) DEFAULT NULL,
  `spotifylink` varchar(100) NOT NULL,
  `imgLink` varchar(255) DEFAULT NULL,
  `likes` int DEFAULT '0',
  `officialplaylist` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`spotifylink`),
  UNIQUE KEY `unique_fields_constraint` (`userid`,`spotifylink`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `playlist`
--

LOCK TABLES `playlist` WRITE;
/*!40000 ALTER TABLE `playlist` DISABLE KEYS */;
INSERT INTO `playlist` VALUES ('109','Trainspotting','0paP1dbf5byXIBWNA6wfNa','https://m.media-amazon.com/images/M/MV5BMzA5Zjc3ZTMtMmU5YS00YTMwLWI4MWUtYTU0YTVmNjVmODZhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@.jpg',0,'2VkRjWE15noVrO25x5SGN8'),('110','Clueless','0pGZVx5u2xmVnpWWPV6AUr','https://m.media-amazon.com/images/M/MV5BMzBmOGQ0NWItOTZjZC00ZDAxLTgyOTEtODJiYWQ2YWNiYWVjXkEyXkFqcGdeQXVyNTE1NjY5Mg@@.jpg',6,'3OrviLrUARxsTuGdWdQTMh'),('110','X','0ymUYlRlPYCaSTBVasgT3z','https://m.media-amazon.com/images/M/MV5BMTJiMmE5YWItOWZjYS00YTg0LWE0MTYtMzg2ZTY4YjNkNDEzXkEyXkFqcGdeQXVyMTAzMDg4NzU0.jpg',0,'1Hc8o20mvQgkj0yxkC7WrS'),('110','The Crow','1NbySmTboOlpRTcQTDjWmF','https://m.media-amazon.com/images/M/MV5BM2Y4ZGVhZjItNjU0OC00MDk1LWI4ZTktYTgwMWJkNDE5OTcxXkEyXkFqcGdeQXVyMTQxNzMzNDI@.jpg',2,'3y7Mwv7UqhABQqsGlzSL6n'),('118','Batman','349PxwPI5Y1NeiErzAxt4T','https://m.media-amazon.com/images/M/MV5BZDNjOGNhN2UtNmNhMC00YjU4LWEzMmUtNzRkM2RjN2RiMjc5XkEyXkFqcGdeQXVyMTU0OTM5ODc1.jpg',1,'1zqfyMgA1aXwVDbukfqSdE'),('110','Hellraiser','3bXhyJvUVqvwuMDr8IntFq','https://m.media-amazon.com/images/M/MV5BOGRlZTdhOGYtODc5NS00YmJkLTkzN2UtZDMyYmRhZWM1NTQwXkEyXkFqcGdeQXVyMzU4Nzk4MDI@.jpg',1,'7kStQ1fN11Yv9tajnZ2vN1'),('115','Wayne\'s World','3CfFxj6IvL80drVKxHl3od','https://m.media-amazon.com/images/M/MV5BMDAyNDY3MjUtYmJjYS00Zjc5LTlhM2MtNzgzYjNlOWVkZjkzL2ltYWdlL2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@.jpg',1,'2P9yFLhHEYnyrQ48CjxvUf'),('117','Austin Powers: International Man of Mystery','3HboadEB7OvIqWofafFA8G','https://m.media-amazon.com/images/M/MV5BMTRhZTY0MDItY2I1Yi00MGE3LTk1ZDEtMjA0ZGZhNDQyNGU0XkEyXkFqcGdeQXVyNTIzOTk5ODM@.jpg',1,'1gNLIaBr1X40wc3RyjeQ8o'),('109','The Menu','3XgmsUB9gjlSWOW6kvIJKH','https://m.media-amazon.com/images/M/MV5BMzdjNjI5MmYtODhiNS00NTcyLWEzZmUtYzVmODM5YzExNDE3XkEyXkFqcGdeQXVyMTAyMjQ3NzQ1.jpg',0,'1rNzQmIHjZCVQEfdOxEItQ'),('108','Evil Dead II','5JYi0hxoMdZwM9Xb6Qokzj','https://m.media-amazon.com/images/M/MV5BMWY3ODZlOGMtNzJmOS00ZTNjLWI3ZWEtZTJhZTk5NDZjYWRjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@.jpg',0,'5VswaCj8hVc9Mx0sAoHfBS'),('119','The Batman','738SepQC1rDUgIdggnyL6Y','https://m.media-amazon.com/images/M/MV5BMDdmMTBiNTYtMDIzNi00NGVlLWIzMDYtZTk3MTQ3NGQxZGEwXkEyXkFqcGdeQXVyMzMwOTU5MDk@.jpg',1,'18nTX27XXEYARGmWMTgD19'),('108','Girl, Interrupted','7796VCM2JrY3qLV39YhuuQ','https://m.media-amazon.com/images/M/MV5BNzdjZDYwM2QtMGNlZS00MGQzLTlhMjctYTU4NWI5MWJlYmQwXkEyXkFqcGdeQXVyMTAwMzUyOTc@.jpg',0,'7qTMQ3yiXeIHocHsJwyeoH'),('109','Mean Girls','7kSMR003iTVJGHl8BLJ0lr','https://m.media-amazon.com/images/M/MV5BMjE1MDQ4MjI1OV5BMl5BanBnXkFtZTcwNzcwODAzMw@@.jpg',0,'5VMeOsRr2wyELrgfz2rkHp');
/*!40000 ALTER TABLE `playlist` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-04-03 16:07:49
