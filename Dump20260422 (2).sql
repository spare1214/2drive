-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: portale_vendita_veicoli
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `annuncio`
--

DROP TABLE IF EXISTS `annuncio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annuncio` (
  `id_annuncio` int NOT NULL AUTO_INCREMENT,
  `titolo` varchar(200) NOT NULL,
  `descrizione` text,
  `data_pubblicazione` date NOT NULL,
  `stato` enum('attivo','venduto','eliminato') DEFAULT 'attivo',
  `visualizzazioni` int DEFAULT '0',
  `id_utente` int DEFAULT NULL,
  `id_veicolo` int DEFAULT NULL,
  `prezzo` decimal(12,2) NOT NULL,
  `telefono_visibile` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_annuncio`),
  KEY `id_utente` (`id_utente`),
  KEY `id_veicolo` (`id_veicolo`),
  KEY `idx_annuncio_stato` (`stato`),
  KEY `idx_annuncio_data` (`data_pubblicazione` DESC),
  CONSTRAINT `annuncio_ibfk_1` FOREIGN KEY (`id_utente`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `annuncio_ibfk_2` FOREIGN KEY (`id_veicolo`) REFERENCES `veicolo` (`id_veicolo`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `annuncio`
--

LOCK TABLES `annuncio` WRITE;
/*!40000 ALTER TABLE `annuncio` DISABLE KEYS */;
INSERT INTO `annuncio` VALUES (1,'Fiat Panda in ottime condizioni','Fiat Panda del 2020, solo 35000 km, perfetta per la città','2026-04-19','attivo',154,2,1,8500.00,1),(2,'Volkswagen Golf automatica','Golf 1.6 TDI, cambio automatico, interni in pelle','2026-04-19','attivo',231,2,2,18500.00,1),(3,'Fiat 500 molto accessoriata','Fiat 500 con cerchi in lega, clima automatico','2026-04-19','attivo',91,3,3,12500.00,0),(4,'Ford Focus diesel','Ford Focus 1.5 TDCI, ottima tenuta di strada','2026-04-19','venduto',45,3,4,11000.00,1),(5,'Toyota Yaris Hybrid','Yaris con motore ibrido, pochissimi km','2026-04-19','attivo',313,4,5,19500.00,1),(6,'Ducati Monster','Ducati Monster 821, tagliandi regolari','2026-04-19','attivo',69,4,6,9500.00,1),(7,'Lamborghini','Nuova ','2026-04-19','venduto',8,5,7,109999.93,1);
/*!40000 ALTER TABLE `annuncio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `tipo_categoria` varchar(50) NOT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'Auto'),(2,'Moto'),(3,'Camper'),(4,'Furgone'),(5,'Camion'),(6,'Scooter'),(7,'Quad'),(8,'Roulotte');
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversazione`
--

DROP TABLE IF EXISTS `conversazione`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversazione` (
  `id_conversazione` int NOT NULL AUTO_INCREMENT,
  `id_annuncio` int NOT NULL,
  `id_acquirente` int NOT NULL,
  `id_venditore` int NOT NULL,
  `ultimo_messaggio` text,
  `ultimo_aggiornamento` datetime DEFAULT NULL,
  PRIMARY KEY (`id_conversazione`),
  KEY `id_annuncio` (`id_annuncio`),
  KEY `id_acquirente` (`id_acquirente`),
  KEY `id_venditore` (`id_venditore`),
  CONSTRAINT `conversazione_ibfk_1` FOREIGN KEY (`id_annuncio`) REFERENCES `annuncio` (`id_annuncio`),
  CONSTRAINT `conversazione_ibfk_2` FOREIGN KEY (`id_acquirente`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `conversazione_ibfk_3` FOREIGN KEY (`id_venditore`) REFERENCES `utente` (`id_utente`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversazione`
--

LOCK TABLES `conversazione` WRITE;
/*!40000 ALTER TABLE `conversazione` DISABLE KEYS */;
INSERT INTO `conversazione` VALUES (1,7,6,5,'ciao','2026-04-22 18:20:08');
/*!40000 ALTER TABLE `conversazione` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `immagine`
--

DROP TABLE IF EXISTS `immagine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `immagine` (
  `id_immagine` int NOT NULL AUTO_INCREMENT,
  `url` varchar(500) NOT NULL,
  `id_annuncio` int DEFAULT NULL,
  PRIMARY KEY (`id_immagine`),
  KEY `id_annuncio` (`id_annuncio`),
  CONSTRAINT `immagine_ibfk_1` FOREIGN KEY (`id_annuncio`) REFERENCES `annuncio` (`id_annuncio`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `immagine`
--

LOCK TABLES `immagine` WRITE;
/*!40000 ALTER TABLE `immagine` DISABLE KEYS */;
INSERT INTO `immagine` VALUES (1,'/static/uploads/panda1.jpg',1),(2,'/static/uploads/golf1.jpg',2),(3,'/static/uploads/5001.jpg',3),(4,'/static/uploads/focus1.jpg',4),(5,'/static/uploads/yaris1.jpg',5),(6,'/static/uploads/monster1.jpg',6);
/*!40000 ALTER TABLE `immagine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marca`
--

DROP TABLE IF EXISTS `marca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marca` (
  `id_marca` int NOT NULL AUTO_INCREMENT,
  `nome_marca` varchar(50) NOT NULL,
  PRIMARY KEY (`id_marca`)
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marca`
--

LOCK TABLES `marca` WRITE;
/*!40000 ALTER TABLE `marca` DISABLE KEYS */;
INSERT INTO `marca` VALUES (1,'Fiat'),(2,'Ford'),(3,'Volkswagen'),(4,'Toyota'),(5,'Renault'),(6,'Peugeot'),(7,'Citroen'),(8,'BMW'),(9,'Mercedes-Benz'),(10,'Audi'),(11,'Opel'),(12,'Nissan'),(13,'Hyundai'),(14,'Kia'),(15,'Honda'),(16,'Suzuki'),(17,'Mazda'),(18,'Volvo'),(19,'Jaguar'),(20,'Land Rover'),(21,'Porsche'),(22,'Ferrari'),(23,'Lamborghini'),(24,'Maserati'),(25,'Alfa Romeo'),(26,'Lancia'),(27,'Abarth'),(28,'DS Automobiles'),(29,'Mini'),(30,'Smart'),(31,'Tesla'),(32,'Skoda'),(33,'Seat'),(34,'Dacia'),(35,'Mitsubishi'),(36,'Subaru'),(37,'Lexus'),(38,'Infiniti'),(39,'Jeep'),(40,'Chrysler'),(41,'Dodge'),(42,'Chevrolet'),(43,'Cadillac'),(44,'Ford USA'),(45,'Ram'),(46,'GMC'),(47,'Hummer'),(48,'Bentley'),(49,'Rolls-Royce'),(50,'Aston Martin'),(51,'McLaren'),(52,'Bugatti'),(53,'Pagani'),(54,'Koenigsegg'),(55,'Rimac'),(56,'Lucid'),(57,'Polestar'),(58,'BYD'),(59,'MG'),(60,'Great Wall'),(61,'Chery'),(62,'Geely'),(63,'Lynk & Co'),(64,'Nio'),(65,'XPeng'),(66,'Hongqi'),(67,'Lotus'),(68,'Caterham'),(69,'Morgan'),(70,'Alpine'),(71,'Vauxhall'),(72,'Haval'),(73,'Proton'),(74,'Perodua'),(75,'SsangYong'),(76,'Mahindra'),(77,'Tata'),(78,'Maruti Suzuki'),(79,'Daihatsu'),(80,'Isuzu'),(81,'Mitsubishi Fuso'),(82,'Iveco'),(83,'MAN'),(84,'Scania'),(85,'Volvo Trucks'),(86,'DAF'),(87,'Renault Trucks'),(88,'Mercedes-Benz Trucks'),(89,'Aprilia'),(90,'Benelli'),(91,'Beta'),(92,'Bimota'),(93,'BMW Motorrad'),(94,'Ducati'),(95,'Energica'),(96,'Gilera'),(97,'Harley-Davidson'),(98,'Honda Motorcycles'),(99,'Husqvarna'),(100,'Hyosung'),(101,'Indian'),(102,'Kawasaki'),(103,'KTM'),(104,'Kymco'),(105,'Lambretta'),(106,'Moto Guzzi'),(107,'Motobi'),(108,'Moto Morini'),(109,'MV Agusta'),(110,'Piaggio'),(111,'Royal Enfield'),(112,'Suzuki Motorcycles'),(113,'Triumph'),(114,'Vespa'),(115,'Victory'),(116,'Yamaha'),(117,'Zero Motorcycles');
/*!40000 ALTER TABLE `marca` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messaggio`
--

DROP TABLE IF EXISTS `messaggio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messaggio` (
  `id_messaggio` int NOT NULL AUTO_INCREMENT,
  `id_mittente` int DEFAULT NULL,
  `id_destinatario` int DEFAULT NULL,
  `id_annuncio` int DEFAULT NULL,
  `contenuto` text NOT NULL,
  `data_invio` datetime NOT NULL,
  `letto` tinyint(1) DEFAULT '0',
  `id_conversazione` int DEFAULT NULL,
  PRIMARY KEY (`id_messaggio`),
  KEY `id_mittente` (`id_mittente`),
  KEY `id_annuncio` (`id_annuncio`),
  KEY `idx_messaggio_destinatario` (`id_destinatario`,`letto`),
  KEY `id_conversazione` (`id_conversazione`),
  CONSTRAINT `messaggio_ibfk_1` FOREIGN KEY (`id_mittente`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `messaggio_ibfk_2` FOREIGN KEY (`id_destinatario`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `messaggio_ibfk_3` FOREIGN KEY (`id_annuncio`) REFERENCES `annuncio` (`id_annuncio`),
  CONSTRAINT `messaggio_ibfk_4` FOREIGN KEY (`id_conversazione`) REFERENCES `conversazione` (`id_conversazione`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messaggio`
--

LOCK TABLES `messaggio` WRITE;
/*!40000 ALTER TABLE `messaggio` DISABLE KEYS */;
INSERT INTO `messaggio` VALUES (1,2,3,3,'Salve, la Fiat 500 è ancora disponibile?','2026-04-19 16:04:29',0,NULL),(2,3,2,1,'Buongiorno, sono interessato alla Panda. È possibile vederla?','2026-04-19 16:04:29',0,NULL),(3,4,2,2,'La Golf è ancora in vendita?','2026-04-19 16:04:29',1,NULL),(4,2,4,5,'Sono interessato alla Yaris Hybrid','2026-04-19 16:04:29',0,NULL),(5,5,2,1,'ciao','2026-04-19 17:13:33',0,NULL),(6,5,2,1,'è','2026-04-19 17:13:37',0,NULL),(7,5,2,1,'facciamo','2026-04-19 17:13:41',0,NULL),(8,5,2,1,'un po','2026-04-19 17:13:44',0,NULL),(9,6,5,7,'ciao','2026-04-19 17:23:43',1,NULL),(10,6,5,7,'mi rispondi','2026-04-19 17:25:18',1,NULL),(11,5,6,7,'cosa vuoi','2026-04-19 17:40:22',1,NULL),(12,6,5,7,'ciao','2026-04-19 21:46:07',1,1),(13,6,5,7,'ciao','2026-04-19 21:46:15',1,1),(14,5,6,7,'ciao','2026-04-19 21:46:37',1,1),(15,6,5,7,'ciao','2026-04-19 21:52:14',1,1),(16,6,5,7,'ciao','2026-04-19 21:52:16',1,1),(17,5,6,7,'ciao','2026-04-19 21:54:17',1,1),(18,6,5,7,'ciao','2026-04-19 21:54:24',1,1),(19,6,5,7,'ciao','2026-04-19 21:54:28',1,1),(20,6,5,7,'ciao','2026-04-19 21:54:34',1,1),(21,6,5,7,'dammi la macchina','2026-04-19 21:54:55',1,1),(22,5,6,7,'no','2026-04-19 21:55:01',1,1),(23,6,5,7,'wtf','2026-04-19 21:55:12',1,1),(24,6,5,7,'bro come on','2026-04-19 21:55:17',1,1),(25,6,5,7,'fuck','2026-04-19 21:56:48',1,1),(26,5,6,7,'o ma vuoi le botte','2026-04-19 22:00:57',1,1),(27,6,5,7,'dai vieni','2026-04-19 22:12:56',1,1),(28,5,6,7,'oggi le prendi','2026-04-19 22:13:19',1,1),(29,5,6,7,'ma fammi un kebab','2026-04-19 22:17:38',1,1),(30,5,6,7,'ciao','2026-04-19 22:18:05',1,1),(31,5,6,7,'ciaoiaoi','2026-04-19 22:22:00',1,1),(32,5,6,7,'ok','2026-04-19 22:22:09',1,1),(33,6,5,7,'addios','2026-04-19 22:22:13',1,1),(34,6,5,7,'kebabbaro','2026-04-19 22:22:20',1,1),(35,5,6,7,'ciao','2026-04-22 18:20:08',0,1);
/*!40000 ALTER TABLE `messaggio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preferiti`
--

DROP TABLE IF EXISTS `preferiti`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preferiti` (
  `id_preferito` int NOT NULL AUTO_INCREMENT,
  `id_utente` int DEFAULT NULL,
  `id_annuncio` int DEFAULT NULL,
  `data_aggiunta` date NOT NULL,
  PRIMARY KEY (`id_preferito`),
  UNIQUE KEY `unique_preferito` (`id_utente`,`id_annuncio`),
  KEY `id_annuncio` (`id_annuncio`),
  KEY `idx_preferiti_utente` (`id_utente`),
  CONSTRAINT `preferiti_ibfk_1` FOREIGN KEY (`id_utente`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `preferiti_ibfk_2` FOREIGN KEY (`id_annuncio`) REFERENCES `annuncio` (`id_annuncio`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preferiti`
--

LOCK TABLES `preferiti` WRITE;
/*!40000 ALTER TABLE `preferiti` DISABLE KEYS */;
INSERT INTO `preferiti` VALUES (1,2,3,'2026-04-19'),(2,2,5,'2026-04-19'),(3,3,1,'2026-04-19'),(4,3,6,'2026-04-19'),(5,4,2,'2026-04-19');
/*!40000 ALTER TABLE `preferiti` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recensione`
--

DROP TABLE IF EXISTS `recensione`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recensione` (
  `id_recensione` int NOT NULL AUTO_INCREMENT,
  `id_recensore` int DEFAULT NULL,
  `id_recensito` int DEFAULT NULL,
  `id_annuncio` int DEFAULT NULL,
  `voto` int DEFAULT NULL,
  `commento` text,
  `data_recensione` datetime DEFAULT NULL,
  PRIMARY KEY (`id_recensione`),
  UNIQUE KEY `unique_recensione` (`id_recensore`,`id_annuncio`),
  KEY `id_recensito` (`id_recensito`),
  KEY `id_annuncio` (`id_annuncio`),
  CONSTRAINT `recensione_ibfk_1` FOREIGN KEY (`id_recensore`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `recensione_ibfk_2` FOREIGN KEY (`id_recensito`) REFERENCES `utente` (`id_utente`),
  CONSTRAINT `recensione_ibfk_3` FOREIGN KEY (`id_annuncio`) REFERENCES `annuncio` (`id_annuncio`),
  CONSTRAINT `recensione_chk_1` CHECK ((`voto` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recensione`
--

LOCK TABLES `recensione` WRITE;
/*!40000 ALTER TABLE `recensione` DISABLE KEYS */;
/*!40000 ALTER TABLE `recensione` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utente`
--

DROP TABLE IF EXISTS `utente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utente` (
  `id_utente` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `nome` varchar(50) NOT NULL,
  `cognome` varchar(50) NOT NULL,
  `data_registrazione` date NOT NULL,
  `verificato` tinyint(1) DEFAULT '0',
  `token_verifica` varchar(255) DEFAULT NULL,
  `media_voti` decimal(3,2) DEFAULT '0.00',
  `totale_recensioni` int DEFAULT '0',
  PRIMARY KEY (`id_utente`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utente`
--

LOCK TABLES `utente` WRITE;
/*!40000 ALTER TABLE `utente` DISABLE KEYS */;
INSERT INTO `utente` VALUES (1,'admin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','admin@portaleveicoli.it','Admin','Portale','2026-04-19',1,NULL,0.00,0),(2,'mariorossi','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','mario.rossi@email.it','Mario','Rossi','2026-04-19',1,NULL,0.00,0),(3,'lucabianchi','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','luca.bianchi@email.it','Luca','Bianchi','2026-04-19',1,NULL,0.00,0),(4,'annaverdi','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','anna.verdi@email.it','Anna','Verdi','2026-04-19',1,NULL,0.00,0),(5,'momo1','03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','momoighir193@gmail.com','MOMO','IGHIR','2026-04-19',1,NULL,0.00,0),(6,'abdul11','03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','ighir.mohamed@einaudicorreggio.it','abdul','lopez','2026-04-19',1,NULL,0.00,0);
/*!40000 ALTER TABLE `utente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `veicolo`
--

DROP TABLE IF EXISTS `veicolo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `veicolo` (
  `id_veicolo` int NOT NULL AUTO_INCREMENT,
  `modello` varchar(100) NOT NULL,
  `anno` int NOT NULL,
  `data_immatricolazione` date DEFAULT NULL,
  `targa` varchar(20) DEFAULT NULL,
  `carburante` varchar(20) DEFAULT NULL,
  `cambio` varchar(20) DEFAULT NULL,
  `chilometraggio` int NOT NULL,
  `colore` varchar(30) DEFAULT NULL,
  `numero_posti` int DEFAULT NULL,
  `luogo` varchar(100) DEFAULT NULL,
  `id_marca` int DEFAULT NULL,
  `id_categoria` int DEFAULT NULL,
  `prezzo` decimal(12,2) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id_veicolo`),
  KEY `idx_veicolo_marca` (`id_marca`),
  KEY `idx_veicolo_categoria` (`id_categoria`),
  CONSTRAINT `veicolo_ibfk_1` FOREIGN KEY (`id_marca`) REFERENCES `marca` (`id_marca`),
  CONSTRAINT `veicolo_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `veicolo`
--

LOCK TABLES `veicolo` WRITE;
/*!40000 ALTER TABLE `veicolo` DISABLE KEYS */;
INSERT INTO `veicolo` VALUES (1,'Panda',2020,NULL,NULL,'benzina','manuale',35000,'Bianco',5,'Milano',1,1,8500.00,'3331234567'),(2,'Golf',2019,NULL,NULL,'diesel','automatico',52000,'Grigio',5,'Roma',3,1,18500.00,'3332345678'),(3,'500',2021,NULL,NULL,'benzina','manuale',15000,'Rosso',4,'Torino',1,1,12500.00,'3333456789'),(4,'Focus',2018,NULL,NULL,'diesel','manuale',78000,'Blu',5,'Napoli',2,1,11000.00,'3334567890'),(5,'Yaris',2022,NULL,NULL,'ibrido','automatico',8000,'Argento',5,'Bologna',4,1,19500.00,'3335678901'),(6,'Monster',2021,NULL,NULL,'benzina','manuale',12000,'Giallo',2,'Milano',106,2,9500.00,'3336789012'),(7,'Urus',2018,'2018-08-01','ABC11HG','diesel','manuale',3000,'Rosso',4,'Milano',23,1,109999.93,'3518587742');
/*!40000 ALTER TABLE `veicolo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-22 18:23:28
