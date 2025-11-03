-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: pet_love
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `additive`
--

DROP TABLE IF EXISTS `additive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `additive` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `en_name` varchar(45) NOT NULL,
  `applicable_range` varchar(45) NOT NULL,
  `type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `en_name_UNIQUE` (`en_name`)
) ENGINE=InnoDB AUTO_INCREMENT=522 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `additive`
--

LOCK TABLES `additive` WRITE;
/*!40000 ALTER TABLE `additive` DISABLE KEYS */;
INSERT INTO `additive` VALUES (1,'辛烯基琥珀酸淀粉钠','Starch Sodium Octenylsuccinate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(2,'二氧化硅','Silicon Dioxide','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(3,'丙三醇','Glycerine','猪、鸡、鱼、犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(4,'硬脂酸','Stearic Acid','猪、牛、家禽、犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(5,'乙基纤维素','Ethyl cellulose','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(6,'聚乙烯醇','Polyvinyl alcohol','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(7,'紫胶','Shellac','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(8,'羟丙基甲基纤维素','Hydroxypropylmethyl cellulose','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(9,'羟丙基纤维素','Hydroxypropylcellulose','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(10,'硬脂酸镁','Magnesium Stearate','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(11,'不溶性聚乙烯聚吡咯烷酮(PVPP)','Insoluble Polyvinylpolypyrrolidone (PVPP)','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(12,'羧甲基淀粉钠','Sodium Carboxymethyl Starch','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(13,'结冷胶','Gellan Gum','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(14,'醋酸酯淀粉','Starch Acetate','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(15,'葡萄糖酸-δ-内酯','Glucono delta-Lactone','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(16,'羟丙基二淀粉磷酸酯','Hydroxypropyl Distarch Phosphate','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(17,'羟丙基淀粉','Hydroxypropyl Starch','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(18,'酪蛋白酸钠','Sodium Caseinate','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(19,'丙二醇脂肪酸酯','Propylene Glycol Esters of Fatty Acids','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(20,'中链甘油三酯','Medium Chain Triglycerides','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(21,'亚麻籽胶','Linseed Gum','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(22,'乙酰化二淀粉磷酸酯','Acetylated Distarch Phosphate','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(23,'麦芽糖醇','Maltitol','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(24,'可得然胶','Curdlan','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(25,'聚葡萄糖','Polydextrose','犬、猫','粘结剂、抗结块剂、稳定剂和乳化剂'),(26,'α-淀粉','alpha-Starch','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(27,'三氧化二铝','Aluminum Oxide','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(28,'可食脂肪酸钙盐','Calcium Salts of Edible Fatty Acids','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(29,'可食用脂肪酸单/双甘油酯','Mono- and Di-glycerides of Edible Fatty Acids','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(30,'硅酸钙','Calcium Silicate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(31,'硅铝酸钠','Sodium Aluminosilicate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(32,'硫酸钙','Calcium Sulfate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(33,'硬脂酸钙','Calcium Stearate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(34,'甘油脂肪酸酯','Glycerol Esters of Fatty Acids','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(35,'聚丙烯酸树脂Ⅱ','Polyacrylic Resin II','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(36,'山梨醇酐单硬脂酸酯','Sorbitan Monostearate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(37,'丙二醇','Propylene Glycol','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(38,'卵磷脂','Lecithin','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(39,'海藻酸钠','Sodium Alginate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(40,'海藻酸钾','Potassium Alginate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(41,'海藻酸铵','Ammonium Alginate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(42,'琼脂','Agar','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(43,'瓜尔胶','Guar Gum','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(44,'阿拉伯树胶','Acacia Gum (Gum Arabic)','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(45,'黄原胶','Xanthan Gum','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(46,'甘露糖醇','Mannitol','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(47,'木质素磺酸盐','Lignosulfonate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(48,'羧甲基纤维素钠','Sodium Carboxymethyl Cellulose','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(49,'聚丙烯酸钠','Sodium Polyacrylate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(50,'山梨醇酐脂肪酸酯','Sorbitan Esters of Fatty Acids','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(51,'蔗糖脂肪酸酯','Sucrose Esters of Fatty Acids','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(52,'单硬脂酸甘油酯','Glycerol Monostearate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(53,'聚乙二醇400','Polyethylene Glycol 400','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(55,'聚乙二醇甘油蓖麻酸酯','Polyethylene Glycol Glyceryl Ricinoleate','养殖动物','粘结剂、抗结块剂、稳定剂和乳化剂'),(56,'卡拉胶','Carrageenan','宠物','粘结剂、抗结块剂、稳定剂和乳化剂'),(57,'决明胶','Cassia Gum','宠物','粘结剂、抗结块剂、稳定剂和乳化剂'),(58,'刺槐豆胶','Carob Bean Gum','宠物','粘结剂、抗结块剂、稳定剂和乳化剂'),(59,'果胶','Pectin','宠物','粘结剂、抗结块剂、稳定剂和乳化剂'),(60,'微晶纤维素','Microcrystalline Cellulose','宠物','粘结剂、抗结块剂、稳定剂和乳化剂'),(61,'氨基酸锌络合物','Zinc Amino Acid Complex','断奶仔猪、肉仔鸡和蛋鸡','矿物元素及其络(螯)合物'),(62,'蛋白铜','Copper Proteinate','养殖动物(反刍动物除外)','矿物元素及其络(螯)合物'),(63,'蛋白铁','Iron Proteinate','养殖动物(反刍动物除外)','矿物元素及其络(螯)合物'),(64,'蛋白锌','Zinc Proteinate','养殖动物(反刍动物除外)','矿物元素及其络(螯)合物'),(65,'蛋白锰','Manganese Proteinate','养殖动物(反刍动物除外)','矿物元素及其络(螯)合物'),(67,'烟酸铬','Chromium Nicotinate','猪、犬、猫','矿物元素及其络(螯)合物'),(68,'酵母铬','Chromium Yeast Complex','猪、犬、猫','矿物元素及其络(螯)合物'),(69,'吡啶甲酸铬','Chromium Tripicolinate','猪、犬、猫','矿物元素及其络(螯)合物'),(70,'蛋氨酸铬','Chromium Methionine Chelate,','猪、犬、猫、泌乳奶牛','矿物元素及其络(螯)合物'),(71,'丙酸铬','Chromium Propionate','猪、犬、猫、奶牛（进口产品）、肉仔鸡','矿物元素及其络(螯)合物'),(72,'甘氨酸锌','Zinc Glycinate','猪、犬、猫','矿物元素及其络(螯)合物'),(73,'丙酸锌','Zinc Propionate','猪、牛和家禽','矿物元素及其络(螯)合物'),(74,'硫酸钾','Potassium Sulfate','反刍动物、畜禽','矿物元素及其络(螯)合物'),(75,'三氧化二铁','Iron Oxide','反刍动物','矿物元素及其络(螯)合物'),(76,'氧化铜','Copper Oxide','反刍动物','矿物元素及其络(螯)合物'),(77,'碳酸钴','Cobalt Carbonate','反刍动物、猫、狗','矿物元素及其络(螯)合物'),(78,'稀土铈壳糖胺螯合盐','Lathanum Chintosan Chelates','畜禽、鱼和虾','矿物元素及其络(螯)合物'),(79,'稀土镧壳糖胺螯合盐','Cerium Chintosan Chelates','畜禽、鱼和虾','矿物元素及其络(螯)合物'),(80,'乳酸锌','Zinc Lactate (α-Hydroxy Propionic Acid Zinc)','生长育肥猪、家禽、犬、猫','矿物元素及其络(螯)合物'),(82,'苏氨酸锌螯合物','Zinc Threoninate Chelate','猪','矿物元素及其络(螯)合物'),(83,'L-硒代蛋氨酸','L-Selenomethionine','肉仔鸡、断奶仔猪、产蛋鸡、淡水鱼、泌乳奶牛','矿物元素及其络(螯)合物'),(84,'一水硫酸锌','Zinc sulfate monohydrate','养殖动物','矿物元素及其络(螯)合物'),(85,'氯化钠','Sodium chloride','养殖动物','矿物元素及其络(螯)合物'),(86,'柠檬酸铜','Cupric Citrate','断奶仔猪','矿物元素及其络(螯)合物'),(87,'碱式氯化锰','Dimanganese Chloride Trihydroxide','肉仔鸡','矿物元素及其络(螯)合物'),(88,'硫酸镁钾','Potassium magnesium sulfate','断奶仔猪','矿物元素及其络(螯)合物'),(89,'氨基酸铁络合物','Iron Amino Acid Complex','家禽和猪','矿物元素及其络(螯)合物'),(90,'氨基酸铜络合物','Copper Amino Acid Complex','畜禽','矿物元素及其络(螯)合物'),(91,'氨基酸锰络合物','Manganese Amino Acid Complex','畜禽','矿物元素及其络(螯)合物'),(92,'碳酸氢钾','Potassium bicarbonate','泌乳奶牛','矿物元素及其络(螯)合物'),(93,'木薯多糖铁','Cassava Polysaccharide Iron','仔猪','矿物元素及其络(螯)合物'),(94,'蔗糖锌','Zinc Sucrose','肉仔鸡','矿物元素及其络(螯)合物'),(95,'蔗糖亚铁','Ferrous sucrose','断奶仔猪','矿物元素及其络(螯)合物'),(96,'右旋糖酐铁','Iron dextran','断奶仔猪','矿物元素及其络(螯)合物'),(97,'红色无定形态单质硒','Red amorphous elemental selenium','肉鸡','矿物元素及其络(螯)合物'),(98,'缬氨酸锌螯合物','Zinc valine chelate','断奶仔猪','矿物元素及其络(螯)合物'),(99,'乙二胺四乙酸铁钠','Sodium ferric ethylenediaminetetraacetate','断奶仔猪','矿物元素及其络(螯)合物'),(100,'葡萄糖酸铜','Copper Gluconate','犬、猫','矿物元素及其络(螯)合物'),(101,'葡萄糖酸锰','Manganese Gluconate','犬、猫','矿物元素及其络(螯)合物'),(102,'葡萄糖酸锌','Zinc Gluconate','犬、猫','矿物元素及其络(螯)合物'),(103,'葡萄糖酸亚铁','Ferrous Gluconate','犬、猫','矿物元素及其络(螯)合物'),(104,'焦磷酸铁','Ferric Pyrophosphate','犬、猫','矿物元素及其络(螯)合物'),(105,'碳酸镁','Magnesium Carbonate','犬、猫','矿物元素及其络(螯)合物'),(106,'甘氨酸钙','Calcium Glycinate','犬、猫','矿物元素及其络(螯)合物'),(107,'二氢碘酸乙二胺','Ethylenediamine Dihydriodide (EDDI)','犬、猫','矿物元素及其络(螯)合物'),(109,'硫酸钠','Sodium Sulfate','养殖动物','矿物元素及其络(螯)合物'),(110,'磷酸二氢钠','Monosodium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(111,'磷酸氢二钠','Disodium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(112,'磷酸二氢钾','Monopotassium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(113,'磷酸氢二钾','Dipotassium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(114,'轻质碳酸钙','Calcium Carbonate','养殖动物','矿物元素及其络(螯)合物'),(115,'氯化钙','Calcium Chloride','养殖动物','矿物元素及其络(螯)合物'),(116,'磷酸氢钙','Dicalcium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(117,'磷酸二氢钙','Monocalcium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(118,'磷酸三钙','Tricalcium Phosphate','养殖动物','矿物元素及其络(螯)合物'),(119,'乳酸钙','Calcium Lactate','养殖动物','矿物元素及其络(螯)合物'),(120,'葡萄糖酸钙','Calcium Gluconate','养殖动物','矿物元素及其络(螯)合物'),(121,'硫酸镁','Magnesium Sulfate','养殖动物','矿物元素及其络(螯)合物'),(122,'氧化镁','Magnesium Oxide','养殖动物','矿物元素及其络(螯)合物'),(123,'氯化镁','Magnesium Chloride','养殖动物','矿物元素及其络(螯)合物'),(124,'柠檬酸亚铁','Ferrous Citrate','养殖动物','矿物元素及其络(螯)合物'),(125,'富马酸亚铁','Ferrous Fumarate','养殖动物','矿物元素及其络(螯)合物'),(126,'乳酸亚铁','Ferrous Lactate','养殖动物','矿物元素及其络(螯)合物'),(127,'硫酸亚铁','Ferrous Sulfate','养殖动物','矿物元素及其络(螯)合物'),(128,'氯化亚铁','Ferrous Chloride','养殖动物','矿物元素及其络(螯)合物'),(129,'氯化铁','Ferric Chloride','养殖动物','矿物元素及其络(螯)合物'),(130,'碳酸亚铁','Ferrous Carbonate','养殖动物','矿物元素及其络(螯)合物'),(131,'氯化铜','Copper Chloride','养殖动物','矿物元素及其络(螯)合物'),(132,'硫酸铜','Copper Sulfate','养殖动物','矿物元素及其络(螯)合物'),(133,'碱式氯化铜','Basic Copper Chloride','养殖动物','矿物元素及其络(螯)合物'),(134,'氧化锌','Zinc Oxide','养殖动物','矿物元素及其络(螯)合物'),(135,'氯化锌','Zinc Chloride','养殖动物','矿物元素及其络(螯)合物'),(136,'碳酸锌','Zinc Carbonate','养殖动物','矿物元素及其络(螯)合物'),(137,'硫酸锌','Zinc Sulfate','养殖动物','矿物元素及其络(螯)合物'),(138,'乙酸锌','Zinc Acetate','养殖动物','矿物元素及其络(螯)合物'),(139,'碱式氯化锌','Basic Zinc Chloride','养殖动物','矿物元素及其络(螯)合物'),(140,'氯化锰','Manganese Chloride','养殖动物','矿物元素及其络(螯)合物'),(141,'氧化锰','Manganese Oxide','养殖动物','矿物元素及其络(螯)合物'),(142,'硫酸锰','Manganese Sulfate','养殖动物','矿物元素及其络(螯)合物'),(143,'碳酸锰','Manganese Carbonate','养殖动物','矿物元素及其络(螯)合物'),(144,'磷酸氢锰','Manganese Phosphate (Dibasic)','养殖动物','矿物元素及其络(螯)合物'),(145,'碘化钾','Potassium Iodide','养殖动物','矿物元素及其络(螯)合物'),(146,'碘化钠','Sodium Iodide','养殖动物','矿物元素及其络(螯)合物'),(147,'碘酸钾','Potassium Iodate','养殖动物','矿物元素及其络(螯)合物'),(148,'碘酸钙','Calcium Iodate','养殖动物','矿物元素及其络(螯)合物'),(149,'氯化钴','Cobalt Chloride','养殖动物','矿物元素及其络(螯)合物'),(150,'乙酸钴','Cobalt Acetate','养殖动物','矿物元素及其络(螯)合物'),(151,'硫酸钴','Cobalt Sulfate','养殖动物','矿物元素及其络(螯)合物'),(152,'亚硒酸钠','Sodium Selenite','养殖动物','矿物元素及其络(螯)合物'),(153,'钼酸钠','Sodium Molybdate','养殖动物','矿物元素及其络(螯)合物'),(154,'蛋氨酸铜络合物','Copper Methionine Complex','养殖动物','矿物元素及其络(螯)合物'),(155,'蛋氨酸铁络合物','Ferric Methionine Complex','养殖动物','矿物元素及其络(螯)合物'),(156,'蛋氨酸锰络合物','Manganese Methionine Complex','养殖动物','矿物元素及其络(螯)合物'),(157,'蛋氨酸锌络合物','Zinc Methionine Complex','养殖动物','矿物元素及其络(螯)合物'),(158,'赖氨酸铜络合物','Copper Lysine Complex','养殖动物','矿物元素及其络(螯)合物'),(159,'赖氨酸锌络合物','Zinc Lysine Complex','养殖动物','矿物元素及其络(螯)合物'),(160,'甘氨酸铜络合物','Copper Glycine Complex','养殖动物','矿物元素及其络(螯)合物'),(161,'甘氨酸铁络合物','Ferrous Glycine Complex','养殖动物','矿物元素及其络(螯)合物'),(162,'酵母铜','Copper Yeast','养殖动物','矿物元素及其络(螯)合物'),(163,'酵母铁','Iron Yeast','养殖动物','矿物元素及其络(螯)合物'),(164,'酵母锰','Manganese Yeast','养殖动物','矿物元素及其络(螯)合物'),(165,'酵母硒','Selenium Yeast','养殖动物','矿物元素及其络(螯)合物'),(170,'D-泛酸钙','D-Calcium Pantothenate','养殖动物','维生素及类维生素'),(171,'L-肉碱酒石酸盐','L-Carnitine- L-Tartrate','宠物','维生素及类维生素'),(172,'维生素K1','Vitamin K1','犬、猫','维生素及类维生素'),(173,'酒石酸氢胆碱','Choline Bitartrate','犬、猫','维生素及类维生素'),(174,'甜菜碱磷酸盐','Betaine phosphate','肉仔鸡','维生素及类维生素'),(176,'维生素A','Vitamin A','养殖动物','维生素及类维生素'),(177,'维生素A乙酸酯','Vitamin A Acetate','养殖动物','维生素及类维生素'),(178,'维生素A棕榈酸酯','Retinol Palmitate','养殖动物','维生素及类维生素'),(179,'β-胡萝卜素','beta-Carotene','养殖动物','维生素及类维生素'),(180,'盐酸硫胺','Thiamin Hydrochloride (Vitamin B1)','养殖动物','维生素及类维生素'),(181,'硝酸硫胺','Thiamin Mononitrate (Vitamin B1)','养殖动物','维生素及类维生素'),(182,'维生素B1','Vitamin B1','养殖动物','维生素及类维生素'),(183,'核黄素','Riboflavin (Vitamin B2)','养殖动物','维生素及类维生素'),(185,'盐酸吡哆醇','Pyridoxine Hydrochloride (Vitamin B6)','养殖动物','维生素及类维生素'),(187,'氰钴胺','Cyanocobalamin (Vitamin B12)','养殖动物','维生素及类维生素'),(189,'L-抗坏血酸','L-Ascorbic Acid','养殖动物','维生素及类维生素'),(190,'维生素C','Vitamin C','养殖动物','维生素及类维生素'),(191,'L-抗坏血酸钙','Calcium L-Ascorbate','养殖动物','维生素及类维生素'),(192,'L-抗坏血酸钠','Sodium L-Ascorbate','养殖动物','维生素及类维生素'),(193,'L-抗坏血酸-2-磷酸酯','L-Ascorbyl-2-Phosphate','养殖动物','维生素及类维生素'),(194,'L-抗坏血酸-6-棕榈酸酯','6-Palmityl-L-Ascorbic Acid','养殖动物','维生素及类维生素'),(195,'维生素D2','Vitamin D2','养殖动物','维生素及类维生素'),(196,'维生素D3','Vitamin D3','养殖动物','维生素及类维生素'),(197,'天然维生素E','Natural Vitamin E','养殖动物','维生素及类维生素'),(198,'dl-α-生育酚','dl-alpha-Tocopherol','养殖动物','维生素及类维生素'),(199,'dl-α-生育酚乙酸酯','dl-alpha-Tocopherol Acetate','养殖动物','维生素及类维生素'),(200,'亚硫酸氢钠甲萘醌（维生素K3）','Menadione Sodium Bisulfite (Vitamin K3)','养殖动物','维生素及类维生素'),(202,'二甲基嘧啶醇亚硫酸甲萘醌','Menadione Dimethylpyrimidinol Bisulfite','养殖动物','维生素及类维生素'),(203,'亚硫酸氢烟酰胺甲萘醌','Menadione Nicotinamide Bisulfite','养殖动物','维生素及类维生素'),(204,'烟酸','Nicotinic Acid','养殖动物','维生素及类维生素'),(205,'烟酰胺','Niacinamide','养殖动物','维生素及类维生素'),(206,'D-泛醇','D-Pantothenyl Alcohol','养殖动物','维生素及类维生素'),(207,'DL-泛酸钙','DL-Calcium Pantothenate','养殖动物','维生素及类维生素'),(208,'叶酸','Folic Acid','养殖动物','维生素及类维生素'),(209,'D-生物素','D-Biotin','养殖动物','维生素及类维生素'),(210,'氯化胆碱','Choline Chloride','养殖动物','维生素及类维生素'),(211,'肌醇','Inositol','养殖动物','维生素及类维生素'),(212,'L-肉碱','L-Carnitine','养殖动物','维生素及类维生素'),(213,'L-肉碱盐酸盐','L-Carnitine Hydrochloride','养殖动物','维生素及类维生素'),(214,'甜菜碱','Betaine','养殖动物','维生素及类维生素'),(215,'甜菜碱盐酸盐','Betaine Hydrochloride','养殖动物','维生素及类维生素'),(216,'乙酸钙','Calcium Acetate','畜禽','防腐剂、防霉剂和酸度调节剂'),(217,'焦磷酸钠','Sodium Pyrophosphate','宠物','防腐剂、防霉剂和酸度调节剂'),(218,'三聚磷酸钠','Sodium Tripolyphosphate','宠物','防腐剂、防霉剂和酸度调节剂'),(219,'六偏磷酸钠','Sodium Hexametaphosphate','宠物','防腐剂、防霉剂和酸度调节剂'),(220,'焦磷酸一氢三钠','Sodium Metabisulphite','宠物','防腐剂、防霉剂和酸度调节剂'),(221,'一氢三钠','Trisodium Monohydrogen Diphosphate','宠物','防腐剂、防霉剂和酸度调节剂'),(222,'焦亚硫酸钠','sodium metabisulfite','宠物、猪','防腐剂、防霉剂和酸度调节剂'),(223,'二甲酸钾','Potassium Diformate','猪','防腐剂、防霉剂和酸度调节剂'),(224,'氯化铵','Ammonium Chloride','反刍动物','防腐剂、防霉剂和酸度调节剂'),(225,'亚硫酸钠','Sodium Sulphite','青贮饲料','防腐剂、防霉剂和酸度调节剂'),(226,'甲酸','Formic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(227,'甲酸钠','Sodium Formate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(228,'亚硝酸钠','Sodium Nitrite','犬、猫','防腐剂、防霉剂和酸度调节剂'),(229,'氢氧化钙','Calcium Hydroxide','犬、猫','防腐剂、防霉剂和酸度调节剂'),(230,'乙二胺四乙酸二钠','Disodium Ethylenediaminetetraacetate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(231,'乳酸钠','Sodium Lactate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(233,'乳酸链球菌素','Nisin','犬、猫','防腐剂、防霉剂和酸度调节剂'),(234,'ε-聚赖氨酸盐酸盐','ε-Polylysine Hydrochloride','犬、猫','防腐剂、防霉剂和酸度调节剂'),(235,'脱氢乙酸','Dehydroacetic Acid','犬、猫','防腐剂、防霉剂和酸度调节剂'),(236,'脱氢乙酸钠','Sodium Dehydroacetate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(237,'琥珀酸','Succinic Acid','犬、猫','防腐剂、防霉剂和酸度调节剂'),(238,'碳酸钾','Potassium Carbonate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(239,'焦磷酸二氢二钠','Disodium Dihydrogen Pyrophosphate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(240,'谷氨酰胺转氨酶','Glutamine Transaminase','犬、猫','防腐剂、防霉剂和酸度调节剂'),(241,'磷酸三钠','Trisodium Phosphate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(242,'葡萄糖酸钠','Sodium Gluconate','犬、猫','防腐剂、防霉剂和酸度调节剂'),(244,'甲酸铵','Ammonium Formate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(245,'甲酸钙','Calcium Formate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(246,'乙酸','Acetic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(247,'双乙酸钠','Sodium Diacetate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(248,'丙酸','Propionic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(249,'丙酸铵','Ammonium Propionate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(250,'丙酸钠','Sodium Propionate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(251,'丙酸钙','Calcium Propionate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(252,'丁酸','Butyric Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(253,'丁酸钠','Sodium Butyrate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(254,'乳酸','Lactic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(255,'苯甲酸','Benzoic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(256,'苯甲酸钠','Sodium Benzoate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(257,'山梨酸','Sorbic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(258,'山梨酸钠','Sodium Sorbate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(259,'山梨酸钾','Potassium Sorbate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(260,'富马酸','Fumaric Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(261,'柠檬酸','Citric Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(262,'柠檬酸钾','Potassium Citrate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(263,'柠檬酸钠','Sodium Citrate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(264,'柠檬酸钙','Calcium Citrate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(265,'酒石酸','Tartaric Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(266,'苹果酸','Malic Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(267,'磷酸','Phosphoric Acid','养殖动物','防腐剂、防霉剂和酸度调节剂'),(268,'氢氧化钠','Sodium Hydroxide','养殖动物','防腐剂、防霉剂和酸度调节剂'),(269,'碳酸氢钠','Sodium Bicarbonate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(270,'氯化钾','Potassium Chloride','养殖动物','防腐剂、防霉剂和酸度调节剂'),(271,'碳酸钠','Sodium Carbonate','养殖动物','防腐剂、防霉剂和酸度调节剂'),(273,'天然叶黄素','Natural Xanthophyll','家禽、水产养殖动物、犬、猫','着色剂'),(274,'虾青素','Astaxanthin','水产养殖动物、观赏鱼、犬、猫','着色剂'),(275,'苋菜红','Amaranth','宠物和观赏鱼','着色剂'),(276,'亮蓝','Brilliant Blue','宠物和观赏鱼','着色剂'),(277,'焦糖色','Caramel Colour','宠物','着色剂'),(278,'胭脂虫红','Carmine Cochineal','犬、猫','着色剂'),(279,'氧化铁红','Iron Oxide Red','犬、猫','着色剂'),(280,'高粱红','Sorghum Red','犬、猫','着色剂'),(281,'红曲红','Monascus Red','犬、猫','着色剂'),(282,'红曲米','Red Kojic Rice','犬、猫','着色剂'),(283,'叶绿素铜钠盐','Chlorophyllin Copper Complex (Sodium Salts)','犬、猫','着色剂'),(284,'栀子蓝','Gardenia Blue','犬、猫','着色剂'),(285,'栀子黄','Gardenia Yellow','犬、猫','着色剂'),(286,'新红','New Red','犬、猫','着色剂'),(287,'酸性红','Carmoisine','犬、猫','着色剂'),(288,'萝卜红','Radish Red','犬、猫','着色剂'),(289,'番茄红素','Lycopene','犬、猫','着色剂'),(301,'柠檬黄','Tartrazine','宠物','着色剂'),(302,'日落黄','Sunset Yellow','宠物','着色剂'),(303,'诱惑红','Allura Red','宠物','着色剂'),(304,'胭脂红','Ponceau 4R','宠物','着色剂'),(305,'靛蓝','Indigotine','宠物','着色剂'),(306,'二氧化钛','Titanium Dioxide','宠物','着色剂'),(308,'赤藓红','Erythrosine','宠物','着色剂'),(309,'辣椒红','Capsanthin','家禽','着色剂'),(310,'β-阿朴-8’-胡萝卜素醛','beta-Apo-8\'-Carotenal','家禽','着色剂'),(311,'β-阿朴-8’-胡萝卜素酸乙酯','beta-Apo-8\'-Carotenoic Acid Ethyl Ester','家禽','着色剂'),(312,'β-胡萝卜素-4','beta-Carotene-4','家禽','着色剂'),(313,'β','beta','家禽','着色剂'),(314,'4-二酮','4-dione','家禽','着色剂'),(315,'斑蝥黄','Canthaxanthin','家禽','着色剂'),(316,'迷迭香提取物','Rosemary Extract','宠物','抗氧化剂'),(317,'硫代二丙酸二月桂酯','Dilauryl Thiodipropionate','犬、猫','抗氧化剂'),(318,'甘草抗氧化物','Antioxidant of Glycyrrhiza','犬、猫','抗氧化剂'),(319,'D-异抗坏血酸','D-Lsoascorbic Acid','犬、猫','抗氧化剂'),(320,'D-异抗坏血酸钠','Sodium D-Lsoascorbate','犬、猫','抗氧化剂'),(321,'植酸','Phytic Acid (Inositol Hexaphosphoric Acid)','犬、猫','抗氧化剂'),(325,'姜黄素','Curcumin','淡水鱼类、肉仔鸡','抗氧化剂'),(326,'阿魏酸','Ferulic acid','虾','抗氧化剂'),(327,'乙氧基喹啉','Ethoxyquin','养殖动物','抗氧化剂'),(328,'丁基羟基茴香醚','Butylated Hydroxyanisole (BHA)','养殖动物','抗氧化剂'),(329,'二丁基羟基甲苯','Butylated Hydroxytoluene (BHT)','养殖动物','抗氧化剂'),(330,'没食子酸丙酯','Propyl Gallate','养殖动物','抗氧化剂'),(331,'特丁基对苯二酚','Tertiary Butyl Hydroquinone (TBHQ)','养殖动物','抗氧化剂'),(332,'茶多酚','Tea Polyphenol','养殖动物','抗氧化剂'),(333,'维生素E','alpha-Tocopherol (Vitamin E)','养殖动物','抗氧化剂'),(335,'尿素','Urea','反刍动物','非蛋白氮'),(336,'碳酸氢铵','Ammonium Bicarbonate','反刍动物','非蛋白氮'),(337,'硫酸铵','Ammonium Sulfate','反刍动物','非蛋白氮'),(338,'液氨','Liquid Ammonia','反刍动物','非蛋白氮'),(339,'磷酸二氢铵','Mono Ammonium Phosphate','反刍动物','非蛋白氮'),(340,'磷酸氢二铵','Diammonium Phosphate','反刍动物','非蛋白氮'),(341,'异丁叉二脲','Isobutylidene Diurea','反刍动物','非蛋白氮'),(342,'磷酸脲','Urea Phosphate','反刍动物','非蛋白氮'),(344,'氨水','Ammonium Hydroxide','反刍动物','非蛋白氮'),(345,'中文名称','English Name','养殖动物','微生物'),(346,'地衣芽孢杆菌','Bacillus licheniformis','养殖动物','微生物'),(347,'枯草芽孢杆菌','Bacillus subtilis','养殖动物','微生物'),(348,'两歧双歧杆菌','Bifidobacterium bifidum','养殖动物','微生物'),(349,'粪肠球菌','Enterococcus faecalis','养殖动物','微生物'),(350,'屎肠球菌','Enterococcus faecium','养殖动物','微生物'),(351,'乳酸肠球菌','Enterococcus lactis','养殖动物','微生物'),(352,'嗜酸乳杆菌','Lactobacillus acidophilus','养殖动物','微生物'),(353,'干酪乳杆菌','Lactobacillus casei','养殖动物','微生物'),(354,'德式乳杆菌乳酸亚种','Lactobacillus delbrueckii subsp. lactis','养殖动物','微生物'),(355,'植物乳杆菌','Lactobacillus plantarum','养殖动物','微生物'),(356,'乳酸片球菌','Pediococcus acidilactici','养殖动物','微生物'),(357,'戊糖片球菌','Pediococcus pentosaceus','养殖动物','微生物'),(358,'产朊假丝酵母','Candida utilis','养殖动物','微生物'),(359,'酿酒酵母','Saccharomyces cerevisiae','养殖动物','微生物'),(360,'沼泽红假单胞菌','Rhodopseudomonas palustris','养殖动物','微生物'),(361,'婴儿双歧杆菌','Bifidobacterium infantis','养殖动物','微生物'),(362,'长双歧杆菌','Bifidobacterium longum','养殖动物','微生物'),(363,'短双歧杆菌','Bifidobacterium breve','养殖动物','微生物'),(364,'青春双歧杆菌','Bifidobacterium adolescentis','养殖动物','微生物'),(365,'嗜热链球菌','Streptococcus thermophilus','养殖动物','微生物'),(366,'罗伊氏乳杆菌','Lactobacillus reuteri','养殖动物','微生物'),(367,'动物双歧杆菌','Bifidobacterium animalis','养殖动物','微生物'),(368,'黑曲霉','Aspergillus niger','养殖动物','微生物'),(369,'米曲霉','Aspergillus oryzae','养殖动物','微生物'),(370,'迟缓芽孢杆菌','Bacillus lentus','养殖动物','微生物'),(371,'短小芽孢杆菌','Bacillus pumilus','养殖动物','微生物'),(372,'纤维二糖乳杆菌','Lactobacillus cellobiosus','养殖动物','微生物'),(373,'发酵乳杆菌','Lactobacillus fermentum','养殖动物','微生物'),(374,'德氏乳杆菌保加利亚亚种','Lactobacillus delbrueckii subsp. bulgaricus','养殖动物','微生物'),(375,'产丙酸丙酸杆菌','Propionibacterium acidipropionicis','青贮饲料、牛饲料','微生物'),(376,'布氏乳杆菌','Lactobacillus buchneri','青贮饲料、牛饲料','微生物'),(378,'副干酪乳杆菌','Lactobacillu paracasei','青贮饲料','微生物'),(379,'凝结芽孢杆菌','Bacillus coagulans','肉鸡、生长育肥猪、水产养殖动物、犬、猫','微生物'),(380,'侧孢短芽孢杆菌','Brevibacillus laterosporus','肉鸡、肉鸭、猪、虾','微生物'),(381,'马克斯克鲁维酵母','Kluyveromyces marxian us (CGMCC 10621)','肉仔鸡','微生物'),(382,'丁酸梭菌','Clostridium butyricum','断奶仔猪、肉仔鸡','微生物'),(383,'约氏乳杆菌','Lactobacillus johnsonii','断奶仔猪、蛋雏鸡','微生物'),(384,'贝莱斯芽孢杆菌','Bacillusvelezensis(CECT5940/CICC11068s)','肉鸡','微生物'),(385,'淀粉酶','Amylase','青贮玉米、玉米、玉米蛋白粉、豆粕、小麦、次粉、大麦、高粱、燕麦、豌豆、木薯、小米、大米','酶制剂'),(386,'α-半乳糖苷酶','α-Galactosidase','豆粕','酶制剂'),(387,'纤维素酶','Cellulase','玉米、大麦、小麦、麦麸、黑麦、高粱','酶制剂'),(388,'β-葡聚糖酶','β-Glucanase','小麦、大麦、菜籽粕、小麦副产物、去壳燕麦、黑麦、黑小麦、高粱','酶制剂'),(389,'葡萄糖氧化酶','Glucose Oxidase','葡萄糖','酶制剂'),(390,'脂肪酶','Lipase','动物或植物源性油脂或脂肪','酶制剂'),(391,'麦芽糖酶','Maltase','麦芽糖','酶制剂'),(392,'β-甘露聚糖酶','β-Mannanase','玉米、豆粕、椰子粕','酶制剂'),(393,'果胶酶','Pectinase','玉米、小麦','酶制剂'),(394,'植酸酶','Phytase','玉米、豆粕等含有植酸的植物籽实及其加工副产品类饲料原料','酶制剂'),(395,'蛋白酶','Protease','植物和动物蛋白','酶制剂'),(396,'角蛋白酶','Keratinase','植物和动物蛋白','酶制剂'),(397,'木聚糖酶','Xylanase','玉米、大麦、黑麦、小麦、高粱、黑小麦、燕麦','酶制剂'),(398,'β-半乳糖苷酶','β-Galactosidase','犬、猫','酶制剂'),(399,'菠萝蛋白酶','Bromelain','犬、猫','酶制剂'),(400,'木瓜蛋白酶','Papain','犬、猫','酶制剂'),(401,'胃蛋白酶','Pepsin','犬、猫','酶制剂'),(402,'胰蛋白酶','Typsin','犬、猫','酶制剂'),(407,'溶菌酶','Lysozyme','仔猪、肉鸡、犬、猫','酶制剂'),(408,'饲用黄曲霉毒素B1分解酶','Aflatoxin B1-detoxifizyme','肉鸡、仔猪','酶制剂'),(409,'胰酶','Pancreatin','肉禽','酶制剂'),(410,'蛋清溶菌酶寡聚体','Egg white lysozyme oligomer','断奶仔猪','酶制剂'),(411,'L-赖氨酸','L-Lysine','养殖动物','氨基酸、氨基酸盐及其类似物'),(412,'液体L-赖氨酸','Liquid L-Lysine','养殖动物','氨基酸、氨基酸盐及其类似物'),(413,'L-赖氨酸盐酸盐','L-Lysine Monohydrochloride','养殖动物','氨基酸、氨基酸盐及其类似物'),(414,'DL-蛋氨酸','DL-Methionine','养殖动物','氨基酸、氨基酸盐及其类似物'),(415,'L-苏氨酸','L-Threonine','养殖动物','氨基酸、氨基酸盐及其类似物'),(416,'L-色氨酸','L-Tryptophan','养殖动物','氨基酸、氨基酸盐及其类似物'),(417,'L-精氨酸','L-Arginine','养殖动物','氨基酸、氨基酸盐及其类似物'),(418,'L-精氨酸盐酸盐','L-Arginine Monohydrochloride','养殖动物','氨基酸、氨基酸盐及其类似物'),(419,'甘氨酸','Glycine','养殖动物','氨基酸、氨基酸盐及其类似物'),(420,'L-酪氨酸','L-Tyrosine','养殖动物','氨基酸、氨基酸盐及其类似物'),(421,'L-丙氨酸','L-Alanine','养殖动物','氨基酸、氨基酸盐及其类似物'),(422,'天冬氨酸','Aspartic Acid','养殖动物','氨基酸、氨基酸盐及其类似物'),(424,'L-亮氨酸','L-Leucine','养殖动物','氨基酸、氨基酸盐及其类似物'),(425,'异亮氨酸','Isoleucine','养殖动物','氨基酸、氨基酸盐及其类似物'),(426,'L-脯氨酸','L-Proline','养殖动物','氨基酸、氨基酸盐及其类似物'),(427,'苯丙氨酸','Phenylalanine','养殖动物','氨基酸、氨基酸盐及其类似物'),(428,'丝氨酸','Serine','养殖动物','氨基酸、氨基酸盐及其类似物'),(429,'L-半胱氨酸','L-Cysteine','养殖动物','氨基酸、氨基酸盐及其类似物'),(430,'L-组氨酸','L-Histidine','养殖动物','氨基酸、氨基酸盐及其类似物'),(431,'谷氨酸','Glutamic Acid','养殖动物','氨基酸、氨基酸盐及其类似物'),(432,'谷氨酰胺','Glutamine','养殖动物','氨基酸、氨基酸盐及其类似物'),(433,'缬氨酸','Valine','养殖动物','氨基酸、氨基酸盐及其类似物'),(434,'胱氨酸','Cystine','养殖动物','氨基酸、氨基酸盐及其类似物'),(435,'牛磺酸','Taurine','养殖动物','氨基酸、氨基酸盐及其类似物'),(436,'半胱胺盐酸盐','Cysteamine Hydrochloride','畜禽','氨基酸、氨基酸盐及其类似物'),(437,'L-半胱胺盐酸盐','L-Cysteine Monohydrochloride','犬、猫','氨基酸、氨基酸盐及其类似物'),(438,'蛋氨酸羟基类似物','Methionine Hydroxy Analogue','猪、鸡、牛、水产养殖动物、犬、猫、鸭','氨基酸、氨基酸盐及其类似物'),(439,'蛋氨酸羟基类似物钙盐','Methionine Hydroxy Analogue Calcium','猪、鸡、牛、水产养殖动物、犬、猫','氨基酸、氨基酸盐及其类似物'),(440,'蛋氨酸羟基类似物异丙酯','Methionine Hydroxy Analogue Isopropyl Ester','反刍动物','氨基酸、氨基酸盐及其类似物'),(441,'N-羟甲基蛋氨酸钙','N-Hydroxymethyl Methionine Calcium','反刍动物','氨基酸、氨基酸盐及其类似物'),(442,'α－环丙氨酸','α-Cycloalanine','鸡','氨基酸、氨基酸盐及其类似物'),(443,'N-氨甲酰谷氨酸','N- Carbamylglutamate','妊娠母猪、花鲈、泌乳奶牛','氨基酸、氨基酸盐及其类似物'),(444,'胍基乙酸','Guanidinoacetic Acid','肉仔鸡、生长育肥猪','氨基酸、氨基酸盐及其类似物'),(445,'索马甜','Thaumatin','养殖动物','调味和诱食物质'),(446,'海藻糖','Trehalose','犬、猫','调味和诱食物质'),(447,'琥珀酸二钠','Disodium Succinate','犬、猫','调味和诱食物质'),(448,'5\'-呈味核苷酸二钠','Disodium 5\'-Ribonucleotide','犬、猫','调味和诱食物质'),(449,'甜菊糖苷','Steviol Glycosides','犬、猫、犊牛、断奶仔猪','调味和诱食物质'),(450,'糖精','Saccharin','猪','调味和诱食物质'),(451,'糖精钙','Calcium Saccharin','猪','调味和诱食物质'),(452,'新甲基橙皮苷二氢查耳酮','Neohesperidin Dihydrochalcone','猪','调味和诱食物质'),(453,'糖精钠','Sodium Saccharin','养殖动物','调味和诱食物质'),(454,'山梨糖醇','Sorbitol','养殖动物','调味和诱食物质'),(455,'食品用香料','Approved Food Flavoring Agents','养殖动物','调味和诱食物质'),(456,'牛至香酚','Oregano Carvacrol','养殖动物','调味和诱食物质'),(457,'谷氨酸钠','Sodium Glutamate','养殖动物','调味和诱食物质'),(458,'5’-肌苷酸二钠','Disodium 5’- Inosinate','养殖动物','调味和诱食物质'),(459,'5’-鸟苷酸二钠','Disodium 5’-Guanylate','养殖动物','调味和诱食物质'),(460,'大蒜素','Garlicin (Allimin)','养殖动物','调味和诱食物质'),(461,'纽甜','Neotame','断奶仔猪','调味和诱食物质'),(462,'二甲基溴化锍','(2-Carboxyethyl) dimethylsulfonium bromide','淡水鱼','调味和诱食物质'),(464,'低聚木糖','Xylo-oligosaccharides','鸡、猪、水产养殖动物、犬、猫','多糖和寡糖'),(466,'低聚壳聚糖','Low-molecular-weight Chitosan','猪、鸡、水产养殖动物、犬、猫','多糖和寡糖'),(467,'半乳甘露寡糖','Galactomanno-oligosaccharides','猪、肉鸡、兔和水产养殖动物','多糖和寡糖'),(468,'果寡糖','Fructo-oligosaccharides','养殖动物','多糖和寡糖'),(469,'甘露寡糖','Manno-oligosaccharides','养殖动物','多糖和寡糖'),(470,'低聚半乳糖','Galacto-oligosaccharides','养殖动物','多糖和寡糖'),(471,'壳寡糖','Chitosan-oligosaccharide','猪、鸡、肉鸭、虹鳟鱼、犬、猫','多糖和寡糖'),(472,'寡聚β-(1-4)-2-氨基-2-脱氧-D-葡萄糖','oligo(beta-(1,4)-2-amino-2-deoxy-D-glucose)','猪、鸡、肉鸭、虹鳟鱼、犬、猫','多糖和寡糖'),(473,'β-1','β-1','水产养殖动物、犬、猫','多糖和寡糖'),(474,'3-D-葡聚糖','3-D-glucan','水产养殖动物、犬、猫','多糖和寡糖'),(475,'N,O-羧甲基壳聚糖','N,O-carboxymethyl chitosan','猪、鸡','多糖和寡糖'),(476,'褐藻酸寡糖','Alginate Oligosaccharides （AOS）','肉鸡、蛋鸡','多糖和寡糖'),(477,'低聚异麦芽糖','lsomaltooligosaccharide (IMO)','蛋鸡、断奶仔猪、犬、猫','多糖和寡糖'),(478,'天然类固醇萨洒皂角苷','YUCCA','养殖动物','其他'),(479,'天然三萜烯皂角苷','Triterpenic saponins','养殖动物','其他'),(480,'二十二碳六烯酸','Doco- sahexaenoic Acid (DHA)','养殖动物','其他'),(481,'糖萜素','Saccharicterpenin','猪和家禽','其他'),(482,'乙酰氧肟酸','Acetohydroxamic Acid','反刍动物','其他'),(483,'苜蓿提取物','Medicago sativa Extract','仔猪、生长育肥猪、肉鸡、犬、猫','其他'),(484,'杜仲叶提取物','Eucommia Ulmoides Extract','生长育肥猪、鱼、虾','其他'),(485,'淫羊藿提取物','Epimedium Extract','鸡、猪、绵羊、奶牛','其他'),(486,'共轭亚油酸','Conjugated Linoleic Acid','仔猪、蛋鸡、犬、猫','其他'),(487,'4,7-二羟基异黄酮','4，7-Dihydroxyisoflavone (Daidzein)','猪、产蛋家禽','其他'),(489,'地顶孢霉培养物','The culture of Acremonium terricola','猪、鸡、泌乳奶牛','其他'),(490,'紫苏籽提取物','Extrat of Perilla frutescens seed','猪、肉鸡和鱼、犬、猫','其他'),(491,'硫酸软骨素','Chondroitin Sulfate','猫、狗','其他'),(492,'植物甾醇','Phytosterol','家禽、生长育肥猪、犬、猫','其他'),(493,'透明质酸','Hyaluronic Acid','犬、猫','其他'),(494,'透明质酸钠','Sodium Hyaluronate','犬、猫','其他'),(495,'乳铁蛋白','Lactoferrin','犬、猫','其他'),(496,'酪蛋白磷酸肽','Casein Phosphopeptides (CPP)','犬、猫','其他'),(497,'酪蛋白钙肽','Casein Calcium Peptide(CCP)','犬、猫','其他'),(498,'二十碳五烯酸','Eicosapentaenoic Acid (EPA)','犬、猫','其他'),(499,'二甲基砜','Methylsulfonylmethane (MSM)','犬、猫','其他'),(500,'硫酸软骨素钠','Sodium Chondroitin Sulfate','犬、猫','其他'),(501,'藤茶黄酮','Total Flavones of Ampelosis grossedentata','鸡','其他'),(502,'胆汁酸','Bile Acids','肉仔鸡、断奶仔猪、淡水鱼类、产蛋鸡、奶牛、虾','其他'),(503,'绿原酸','Chlorogenic acid','肉仔鸡','其他'),(504,'植物炭黑','Plant Carbon','仔猪、肉鸡、淡水鱼','其他'),(505,'吡咯并喹啉醌二钠','Pyrroloquinoline Quinone Disodium salt','肉仔鸡<br/>断奶仔猪','其他'),(506,'水飞蓟宾','Silybin','淡水鱼、肉鸡','其他'),(507,'鞣酸蛋白','Albumin tannate','断奶仔猪','其他'),(508,'三丁酸甘油酯','Tributyrin','肉仔鸡','其他'),(509,'万寿菊提取物','Marigold extract','肉仔鸡','其他'),(510,'枯草三十七肽','Sublancin','肉鸡','其他'),(511,'腺苷七肽','Johnisin-C','断奶仔猪','其他'),(512,'甜叶菊提取物','Stevia extract','肉仔鸡和断奶仔猪','其他'),(514,'卫矛醇','Dulcitol','肉仔鸡，生长育肥猪','其他'),(515,'异绿原酸钠','Sodium isochlorogenic acid','断奶仔猪、产蛋鸡','其他'),(516,'红三叶草提取物','Red clover extracts','成年奶牛和育成期奶牛','植物提取物'),(517,'石香薷提取物','Mosla chinensis Maxim extract','肉仔鸡','植物提取物'),(518,'茯苓提取物','Poriacocosextract','生长育肥猪，肉仔鸡','植物提取物'),(519,'没食子酸','Gallic acid ','断奶仔猪','植物提取物'),(520,'甘草提取物','Glycyrrhiza uralensis Fisch.extract','肉仔鸡','植物提取物');
/*!40000 ALTER TABLE `additive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$lk5t9lo7MXLiDidcujMcQg$ow6a4kfOS2nD7euKDzCdiLJCMjxPrcUO9Cyb/JVE+Jg=','2025-10-21 07:01:38.738210',1,'yuanqh23','','','3157085660@qq.com',1,1,'2025-10-21 07:01:17.256348');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-10-21 06:59:21.784960'),(2,'auth','0001_initial','2025-10-21 06:59:22.954487'),(3,'admin','0001_initial','2025-10-21 06:59:23.230634'),(4,'admin','0002_logentry_remove_auto_add','2025-10-21 06:59:23.242116'),(5,'admin','0003_logentry_add_action_flag_choices','2025-10-21 06:59:23.252735'),(6,'contenttypes','0002_remove_content_type_name','2025-10-21 06:59:23.432906'),(7,'auth','0002_alter_permission_name_max_length','2025-10-21 06:59:23.562459'),(8,'auth','0003_alter_user_email_max_length','2025-10-21 06:59:23.596090'),(9,'auth','0004_alter_user_username_opts','2025-10-21 06:59:23.607371'),(10,'auth','0005_alter_user_last_login_null','2025-10-21 06:59:23.704596'),(11,'auth','0006_require_contenttypes_0002','2025-10-21 06:59:23.710981'),(12,'auth','0007_alter_validators_add_error_messages','2025-10-21 06:59:23.723418'),(13,'auth','0008_alter_user_username_max_length','2025-10-21 06:59:23.845732'),(14,'auth','0009_alter_user_last_name_max_length','2025-10-21 06:59:23.962655'),(15,'auth','0010_alter_group_name_max_length','2025-10-21 06:59:23.990698'),(16,'auth','0011_update_proxy_permissions','2025-10-21 06:59:24.003529'),(17,'auth','0012_alter_user_first_name_max_length','2025-10-21 06:59:24.123409'),(18,'sessions','0001_initial','2025-10-21 06:59:24.198990'),(19,'additive','0001_initial','2025-10-23 04:41:40.131852');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('br6xm75btisqn5dwo90myfsemyiehv2b','.eJxVjEEOwiAQRe_C2hCgAzgu3fcMZGCoVA0kpV0Z765NutDtf-_9lwi0rSVsPS9hZnERWpx-t0jpkesO-E711mRqdV3mKHdFHrTLsXF-Xg_376BQL9_aZAt8BuVhsB7AWSCXpwEni2lQ4DNqhQmZnEYVTSJibb1BNIrBkxXvD7MmNr8:1vB6NG:nvo2K-AT5BMab1DcmZvdbl2hzzLm-BSYlVHUr0mf2EM','2025-11-04 07:01:38.745214');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingredient`
--

DROP TABLE IF EXISTS `ingredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredient` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `type` varchar(45) NOT NULL,
  `label` varchar(45) DEFAULT NULL,
  `desc` varchar(400) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=410 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredient`
--

LOCK TABLES `ingredient` WRITE;
/*!40000 ALTER TABLE `ingredient` DISABLE KEYS */;
INSERT INTO `ingredient` VALUES (1,'大蒜渣','块茎、块根及其加工产品','粗纤维\n水分','大蒜取油后的副产品。'),(2,'甘薯渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','甘薯提取淀粉后的副产品。'),(3,'胡萝卜渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','胡萝卜经榨汁或提取胡萝卜素后获得的副产品。'),(4,'菊苣渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','菊苣制取菊糖或香料后的副产品，由浸提或压榨后的菊苣片组成。'),(5,'菊芋渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','菊芋提取菊糖后的副产物。'),(6,'马铃薯蛋白粉','块茎、块根及其加工产品','粗蛋白质','马铃薯提取淀粉后经干燥获得的粉状产品。主要成分为蛋白质。'),(7,'马铃薯渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','马铃薯经提取淀粉和蛋白后的副产物。'),(8,'木薯渣','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','木薯提取淀粉后的副产物。'),(9,'甜菜粕颗粒','块茎、块根及其加工产品','粗纤维\n粗灰分\n水分','以甜菜粕为原料，添加废糖蜜等辅料经制粒形成的产品。'),(10,'甜菜糖蜜','块茎、块根及其加工产品','总糖\n粗灰分\n水分','从甜菜中提糖后获得的液体副产品。'),(11,'瓜籽','块茎、块根及其加工产品','粗蛋白','可食用瓜类的籽实经干燥等工艺加工获得的产品，产品名称应标明使用原料的来源，如：南瓜籽。'),(12,'酿酒酵母发酵白酒糟','其它饲料原料','粗蛋白\n粗纤维\n酸溶蛋白\n木质素','以鲜白酒糟为基质，经酿酒酵母固体发酵、自溶、干燥、粉碎后得到的产品。'),(13,'啤酒酵母粉','其它饲料原料','粗蛋白质\n粗灰分','啤酒发酵过程中产生的废弃酵母，以啤酒酵母细胞为主要组分，经干燥获得的产品。'),(14,'啤酒酵母泥','其它饲料原料','粗蛋白质\n粗灰分','啤酒发酵中产生的泥浆状废弃酵母，以啤酒酵母细胞为主且含有少量啤酒。'),(15,'食品酵母粉','其它饲料原料','粗蛋白质\n粗灰分','食品酵母生产过程中产生的废弃酵母经干燥获得的产品，以酿酒酵母细胞为主要组分。'),(16,'酿酒酵母培养物','其它饲料原料','粗蛋白质\n粗灰分\n粗纤维\n甘露聚糖','以酿酒酵母（Saccharomyces cerevisiae）为菌种发酵获得的产品。'),(17,'谷物酒糟类产品','其它饲料原料','','见第1.5'),(18,'葡萄酒糟','其它饲料原料','粗蛋白质\n粗灰分','工业法生产葡萄汁的副产物，由分离发酵葡萄汁后的液体/糊状物组成。'),(19,'葡萄酒糟泥','其它饲料原料','粗蛋白质\n粗灰分','工业法生产葡萄汁的副产物，由分离发酵葡萄汁后的液体/糊状物组成。'),(20,'甜菜糖蜜酵母发酵浓缩液','其它饲料原料','钾\n盐分\n甜菜碱\n非蛋白氮','以甜菜糖蜜为原料，经液体发酵生产酵母后的残液再经浓缩得到的产品。'),(21,'扁豆','豆科作物籽实及其加工产品','','豆科蝶形花亚科扁豆属扁豆（Lablab purpureus L.）的籽实。'),(22,'去皮扁豆','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','扁豆籽实去皮后的产品。'),(23,'菜豆','豆科作物籽实及其加工产品','','豆科菜豆属菜豆（Phaseolus vulgaris L.）的籽实。'),(24,'芸豆','豆科作物籽实及其加工产品','','豆科菜豆属菜豆（Phaseolus vulgaris L.）的籽实。'),(25,'蚕豆','豆科作物籽实及其加工产品','','豆科野豌豆属蚕豆（Vicia faba L.）的籽实。'),(26,'蚕豆粉浆蛋白粉','豆科作物籽实及其加工产品','粗蛋白质','用蚕豆生产淀粉时，从其粉浆中分离出淀粉后经干燥获得的粉状副产品。'),(27,'蚕豆皮','豆科作物籽实及其加工产品','粗纤维\n粗灰分','蚕豆籽实经去皮工艺脱下的种皮。'),(28,'去皮蚕豆','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','蚕豆籽实去皮后的产品。'),(29,'压片蚕豆','豆科作物籽实及其加工产品','粗蛋白质','去皮蚕豆经汽蒸、碾压处理获得的产品。'),(30,'瓜尔豆','豆科作物籽实及其加工产品','','豆科瓜尔豆属（Cyamopsis tetragonolobaL.）的籽实。'),(31,'瓜尔豆粕','豆科作物籽实及其加工产品','粗蛋白质','瓜尔豆籽实经浸提制取瓜尔豆胶后的副产品。'),(32,'红豆皮','豆科作物籽实及其加工产品','粗纤维\n粗灰分','红豆籽实经脱皮工艺脱下的种皮。'),(33,'红豆渣','豆科作物籽实及其加工产品','粗纤维\n粗灰分\n水分','红豆经湿法提取淀粉和蛋白后所得的副产品。'),(34,'绿豆','豆科作物籽实及其加工产品','','豆科豇豆属绿豆（Vigna radiata L.）的籽实。'),(35,'绿豆粉浆蛋白粉','豆科作物籽实及其加工产品','粗蛋白质','用绿豆生产淀粉时，从其粉浆中分离出淀粉后经干燥获得的粉状副产品。'),(36,'绿豆皮','豆科作物籽实及其加工产品','粗纤维\n粗灰分','绿豆籽实经去皮工艺脱下的种皮。'),(37,'绿豆渣','豆科作物籽实及其加工产品','粗纤维\n粗灰分\n水分','绿豆经湿法提取淀粉和蛋白后所得的副产品。'),(38,'豌豆','豆科作物籽实及其加工产品','','豆科豌豆属豌豆（Pisum sativum L.）的籽实。可经瘤胃保护。'),(39,'去皮豌豆','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','豌豆籽实去皮后的产品。'),(40,'豌豆次粉','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','豌豆制粉过程中获得的副产品，主要由胚乳和少量豆皮组成。'),(41,'豌豆粉','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','豌豆经粉碎所得的产品。'),(42,'豌豆粉浆蛋白粉','豆科作物籽实及其加工产品','粗蛋白质','用豌豆生产淀粉时，从其粉浆中分离出淀粉后经干燥获得的粉状副产品。'),(43,'豌豆皮','豆科作物籽实及其加工产品','粗纤维\n粗灰分','豌豆籽实经去皮工艺脱下的种皮。'),(44,'豌豆纤维','豆科作物籽实及其加工产品','粗纤维','从豌豆中提取的纤维物质。'),(45,'豌豆渣','豆科作物籽实及其加工产品','粗纤维\n粗灰分\n水分','豌豆经湿法提取淀粉和蛋白后所得的副产品。'),(46,'压片豌豆','豆科作物籽实及其加工产品','粗蛋白质','去皮豌豆经汽蒸、碾压获得的产品。'),(47,'鹰嘴豆','豆科作物籽实及其加工产品','','豆科鹰嘴豆属鹰嘴豆（Cicer arietinum L.）的籽实。'),(48,'去皮羽扇豆','豆科作物籽实及其加工产品','粗蛋白质\n粗纤维','羽扇豆籽实经去皮后的产品。'),(49,'羽扇豆皮','豆科作物籽实及其加工产品','粗纤维\n粗灰分','羽扇豆籽实经去皮工艺脱下的种皮。'),(50,'羽扇豆渣','豆科作物籽实及其加工产品','粗纤维\n粗灰分\n水分','羽扇豆提取蛋白或寡糖组分后获得的副产品。'),(51,'豆荚','豆科作物籽实及其加工产品','粗纤维','本目录所列豆科植物籽实的豆荚，产品名称应标明原料的来源，如：豌豆荚。'),(52,'豆荚粉','豆科作物籽实及其加工产品','粗纤维','本目录所列豆科植物籽实的豆荚经粉碎获得的产品，产品名称应标明原料的来源，如：角豆荚粉。'),(53,'兵豆','豆科作物籽实及其加工产品','','豆科兵豆属兵豆(Lens culinaris)的籽实。'),(54,'小扁豆','豆科作物籽实及其加工产品','','豆科兵豆属兵豆(Lens culinaris)的籽实。'),(55,'扁桃仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','扁桃仁或杏仁饼经浸提取油后的副产品。'),(56,'扁桃杏仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','扁桃仁或杏仁饼经浸提取油后的副产品。'),(57,'扁桃仁油','油料籽实及其加工产品','酸价\n过氧化值','扁桃仁或杏仁经压榨或浸提制取的油脂。产品须由有资质的食品生产企业提供。'),(58,'扁桃杏仁油','油料籽实及其加工产品','酸价\n过氧化值','扁桃仁或杏仁经压榨或浸提制取的油脂。产品须由有资质的食品生产企业提供。'),(59,'菜籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪','菜籽经压榨取油后的副产品。可经瘤胃保护。'),(60,'菜饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪','菜籽经压榨取油后的副产品。可经瘤胃保护。'),(61,'菜籽蛋白','油料籽实及其加工产品','粗蛋白质','利用菜籽或菜籽粕生产的蛋白质含量不低于50％（以干基计）的产品。'),(62,'菜籽皮','油料籽实及其加工产品','粗脂肪\n粗纤维','油菜籽经脱皮工艺脱下的种皮。'),(63,'菜籽油','油料籽实及其加工产品','酸价\n过氧化值','菜籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(64,'菜油','油料籽实及其加工产品','酸价\n过氧化值','菜籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(65,'膨化菜籽','油料籽实及其加工产品','粗蛋白质\n粗脂肪','菜籽在一定温度和压力条件下，经膨化处理获得的产品。可经瘤胃保护。'),(66,'大豆','油料籽实及其加工产品','','豆科草本植物栽培大豆（Glycine max. L. Merr.）的种子。'),(67,'大豆磷脂油','油料籽实及其加工产品','丙酮不溶物\n粗脂肪\n酸价\n水分','在大豆原油脱胶过程中分离出的、经真空脱水获得的含油磷脂。'),(68,'大豆磷脂油粉','油料籽实及其加工产品','丙酮不溶物\n粗脂肪\n酸价\n水分','大豆磷脂油与载体（玉米粉、玉米芯粉、稻壳粉、麸皮）混合、干燥后的产品，粗脂肪≥50%'),(69,'大豆酶解蛋白','油料籽实及其加工产品','酸溶蛋白（三氯乙酸可溶蛋白）\n粗蛋白质\n粗灰分\n钙','大豆或大豆加工产品（脱皮豆粕/大豆浓缩蛋白）经酶水解、干燥后获得的产品。'),(70,'大豆浓缩蛋白','油料籽实及其加工产品','粗蛋白质','低温大豆粕除去其中的非蛋白成分后获得的蛋白质含量不低于65%（以干基计）的产品。'),(71,'大豆胚芽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆胚芽脱油后的产品。'),(72,'大豆胚芽粉','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆胚芽脱油后的产品。'),(73,'大豆胚芽油','油料籽实及其加工产品','酸价\n过氧化值','大豆胚芽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(74,'大豆皮','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆经脱皮工艺脱下的种皮。'),(75,'大豆筛余物','油料籽实及其加工产品','粗纤维\n粗灰分','大豆籽实清理过程中筛选出的瘪的或破碎的籽实、种皮和外壳。'),(76,'大豆纤维','油料籽实及其加工产品','粗纤维','从大豆中提取的纤维物质。'),(77,'大豆油','油料籽实及其加工产品','酸价\n过氧化值','大豆经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(78,'豆油','油料籽实及其加工产品','酸价\n过氧化值','大豆经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(79,'豆饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪','大豆籽粒经压榨取油后的副产品。可经瘤胃保护。'),(80,'大豆饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪','大豆籽粒经压榨取油后的副产品。可经瘤胃保护。'),(81,'大豆粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆胚片经膨胀浸提制油工艺提取油后获得的产品。可经瘤胃保护。'),(82,'豆渣','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆经浸泡、碾磨、加工成豆制品或提取蛋白后的副产品。'),(83,'大豆渣','油料籽实及其加工产品','粗蛋白质\n粗纤维','大豆经浸泡、碾磨、加工成豆制品或提取蛋白后的副产品。'),(84,'烘烤大豆','油料籽实及其加工产品','','烘烤的大豆或将其粉碎后的产品。可经瘤胃保护。'),(85,'烘烤大豆粉','油料籽实及其加工产品','','烘烤的大豆或将其粉碎后的产品。可经瘤胃保护。'),(86,'膨化大豆','油料籽实及其加工产品','粗蛋白质\n粗脂肪','全脂大豆经清理、破碎（磨碎）、膨化处理获得的产品。'),(87,'膨化大豆粉','油料籽实及其加工产品','粗蛋白质\n粗脂肪','全脂大豆经清理、破碎（磨碎）、膨化处理获得的产品。'),(88,'膨化大豆蛋白','油料籽实及其加工产品','粗蛋白质','大豆分离蛋白、大豆浓缩蛋白在一定温度和压力条件下，经膨化处理获得的产品。'),(89,'大豆组织蛋白','油料籽实及其加工产品','粗蛋白质','大豆分离蛋白、大豆浓缩蛋白在一定温度和压力条件下，经膨化处理获得的产品。'),(90,'膨化豆粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','豆粕经膨化处理后获得的产品。'),(91,'番茄籽油','油料籽实及其加工产品','酸价\n过氧化值','番茄籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(92,'橄榄粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','油橄榄饼经浸提取油后获得的副产品。'),(93,'油橄榄粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','油橄榄饼经浸提取油后获得的副产品。'),(94,'橄榄油','油料籽实及其加工产品','酸价\n过氧化值','橄榄经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(95,'核桃仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','核桃仁经预压浸提或直接溶剂浸提取油后获得的副产品，或由核桃仁饼浸提取油后获得的副产品。'),(96,'核桃仁油','油料籽实及其加工产品','酸价\n过氧化值','核桃仁经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(97,'红花籽','油料籽实及其加工产品','','菊科植物红花（Carthamus tinctorius L.）的种子。'),(98,'红花籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','红花籽(仁)经压榨取油后的副产品。'),(99,'红花籽壳','油料籽实及其加工产品','粗纤维','红花籽脱壳取仁后的产品。'),(100,'红花籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','红花籽(仁)经浸提取油后的副产品。'),(101,'红花籽油','油料籽实及其加工产品','酸价\n过氧化值','红花籽（仁）经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(102,'花椒籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','花椒籽经压榨取油后的副产品。'),(103,'花椒饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','花椒籽经压榨取油后的副产品。'),(104,'花椒籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','花椒籽经预压浸提或直接溶剂浸提取油后获得的副产品，或由花椒饼浸提取油获得的副产品。'),(105,'花椒粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','花椒籽经预压浸提或直接溶剂浸提取油后获得的副产品，或由花椒饼浸提取油获得的副产品。'),(106,'花椒籽油','油料籽实及其加工产品','酸价\n过氧化值','花椒籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(107,'花生饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','脱壳或部分脱壳（含壳率≤30%）的花生经压榨取油后的副产品。'),(108,'花生仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','脱壳或部分脱壳（含壳率≤30%）的花生经压榨取油后的副产品。'),(109,'花生蛋白','油料籽实及其加工产品','粗蛋白质\n粗纤维','由花生及花生粕生产的蛋白质含量不低于65％（以干基计）的产品。'),(110,'花生红衣','油料籽实及其加工产品','粗纤维','花生仁外衣，含有丰富单宁和硫胺。'),(111,'花生壳','油料籽实及其加工产品','粗纤维','花生的外壳。'),(112,'花生粕','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','花生经预压浸提或直接溶剂浸提取油后获得的副产品，或由花生饼浸提取油获得的副产品。'),(113,'花生仁粕','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','花生经预压浸提或直接溶剂浸提取油后获得的副产品，或由花生饼浸提取油获得的副产品。'),(114,'花生油','油料籽实及其加工产品','酸价\n过氧化值','花生（仁）经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(115,'可可饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','脱壳后的可可（Theobroma cacao L.）豆经压榨取油后的副产品，可经粉碎。'),(116,'可可饼粉','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','脱壳后的可可（Theobroma cacao L.）豆经压榨取油后的副产品，可经粉碎。'),(117,'可可脂','油料籽实及其加工产品','酸价\n过氧化值','可可豆经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(118,'可可油','油料籽实及其加工产品','酸价\n过氧化值','可可豆经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(119,'葵花头粉','油料籽实及其加工产品','粗纤维\n粗灰分','葵花盘脱除葵花籽后剩余物粉碎烘干的产品。'),(120,'向日葵盘粉','油料籽实及其加工产品','粗纤维\n粗灰分','葵花盘脱除葵花籽后剩余物粉碎烘干的产品。'),(121,'葵花籽壳','油料籽实及其加工产品','粗纤维','向日葵籽的外壳。'),(122,'向日葵壳','油料籽实及其加工产品','粗纤维','向日葵籽的外壳。'),(123,'向日葵籽仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','部分脱壳的向日葵籽经压榨取油后的副产品。'),(124,'葵花籽仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','部分脱壳的向日葵籽经压榨取油后的副产品。'),(125,'向日葵籽仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','部分脱壳的向日葵籽菜籽经预压浸提或直接溶剂浸提取油后获得的副产品。可经瘤胃保护。'),(126,'葵花籽仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','部分脱壳的向日葵籽菜籽经预压浸提或直接溶剂浸提取油后获得的副产品。可经瘤胃保护。'),(127,'向日葵籽油','油料籽实及其加工产品','酸价\n过氧化值','向日葵籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(128,'葵花籽油','油料籽实及其加工产品','酸价\n过氧化值','向日葵籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(129,'棉仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','按脱壳程度，含壳量低的棉籽饼称为棉仁、饼。'),(130,'棉籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','棉籽经脱绒、脱壳和压榨取油后的副产品。'),(131,'棉饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','棉籽经脱绒、脱壳和压榨取油后的副产品。'),(132,'棉籽蛋白','油料籽实及其加工产品','粗蛋白质\n游离棉酚','由棉籽或棉籽粕生产的粗蛋白质含量在50％以上的产品。'),(133,'棉籽壳','油料籽实及其加工产品','粗纤维','棉籽剥壳，以及仁壳分离后以壳为主的产品。'),(134,'棉籽酶解蛋白','油料籽实及其加工产品','酸溶蛋白(三氯乙酸可溶蛋白)\n粗蛋白质\n粗灰分\n游离棉酚\n钙','棉籽或棉籽蛋白粉经酶水解、干燥后获得的产品。'),(135,'棉籽油','油料籽实及其加工产品','酸价\n过氧化值','棉籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(136,'棉油','油料籽实及其加工产品','酸价\n过氧化值','棉籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(137,'木棉籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','木棉（Bombax malabaricum DC.）籽经压榨取油后的副产品。'),(138,'木棉籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','木棉籽经预压浸提或直接溶剂浸提取油后获得的副产品，或由木棉籽饼浸提取油获得的副产品。'),(139,'木棉籽油','油料籽实及其加工产品','酸价\n过氧化值','木棉籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(140,'葡萄籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','葡萄（Vitis vinifera L.）籽经浸提取油后的副产品。'),(141,'葡萄籽油','油料籽实及其加工产品','酸价\n过氧化值','葡萄籽经浸提制取的油。产品须由有资质的食品生产企业提供。'),(142,'沙棘籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','沙棘（Hippophae rhamnoides L.）籽经压榨取油后的副产品。'),(143,'沙棘籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','沙棘籽经浸提或超临界萃取取油后的副产品。'),(144,'沙棘籽油','油料籽实及其加工产品','酸价\n过氧化值','沙棘籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(145,'酸枣油','油料籽实及其加工产品','酸价\n过氧化值','酸枣果仁经浸提制取的油。产品须由有资质的食品生产企业提供。'),(146,'文冠果油','油料籽实及其加工产品','酸价\n过氧化值','文冠果种子经压榨制取的油。产品须由有资质的食品生产企业提供。'),(147,'亚麻籽','油料籽实及其加工产品','','亚麻（Linum usitatissimum L.）的种子。可经瘤胃保护。'),(148,'胡麻籽','油料籽实及其加工产品','','亚麻（Linum usitatissimum L.）的种子。可经瘤胃保护。'),(149,'亚麻饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','亚麻籽经压榨取油后的副产品。'),(150,'亚麻籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','亚麻籽经压榨取油后的副产品。'),(151,'亚麻仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','亚麻籽经压榨取油后的副产品。'),(152,'胡麻饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','亚麻籽经压榨取油后的副产品。'),(153,'亚麻粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','亚麻籽经浸提取油后的副产品。'),(154,'亚麻籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','亚麻籽经浸提取油后的副产品。'),(155,'亚麻仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','亚麻籽经浸提取油后的副产品。'),(156,'胡麻粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','亚麻籽经浸提取油后的副产品。'),(157,'亚麻籽油','油料籽实及其加工产品','酸价\n过氧化值','亚麻籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(158,'亚麻籽粉','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','亚麻籽经制粉工艺获得的粉状产品。'),(159,'椰子粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','以干燥的椰子胚乳 (即椰肉)为原料，经预榨以及溶剂浸提取油后的副产品。'),(160,'椰子油','油料籽实及其加工产品','酸价\n过氧化值','椰子胚乳 (即椰肉)经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(161,'棕榈饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','棕榈仁经压榨取油后的副产品。'),(162,'棕榈仁饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','棕榈仁经压榨取油后的副产品。'),(163,'棕榈粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','棕榈仁经浸提取油后的副产品。'),(164,'棕榈仁粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','棕榈仁经浸提取油后的副产品。'),(165,'棕榈仁','油料籽实及其加工产品','','油棕榈果实脱壳后的果仁。'),(166,'棕榈仁油','油料籽实及其加工产品','酸价\n过氧化值','棕榈仁经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(167,'棕榈油','油料籽实及其加工产品','酸价\n过氧化值','棕榈果肉经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(168,'月见草籽','油料籽实及其加工产品','','月见草（Oenothera biennis L.）籽实。'),(169,'月见草籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','月见草籽经冷榨、浸提取油后的副产品。'),(170,'月见草籽油','油料籽实及其加工产品','酸价\n过氧化值','月见草籽经冷榨、浸提制取的油。产品须由有资质的食品生产企业提供。'),(171,'芝麻籽','油料籽实及其加工产品','','芝麻（Sesamum indicum L.）种子。'),(172,'芝麻饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','芝麻籽经压榨取油后的副产品。'),(173,'油麻饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','芝麻籽经压榨取油后的副产品。'),(174,'芝麻粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','芝麻籽经预压浸提或直接溶剂浸提取油后的副产品，或芝麻籽饼浸提取油后的副产品。'),(175,'芝麻油','油料籽实及其加工产品','酸价\n过氧化值','芝麻籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(176,'紫苏籽','油料籽实及其加工产品','','紫苏（Perilla frutescens L.）的籽实。'),(177,'紫苏饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','紫苏籽经压榨取油后的副产品。'),(178,'紫苏籽饼','油料籽实及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','紫苏籽经压榨取油后的副产品。'),(179,'紫苏粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','紫苏籽或紫苏籽饼经浸提取油后的副产品。'),(180,'紫苏籽粕','油料籽实及其加工产品','粗蛋白质\n粗纤维','紫苏籽或紫苏籽饼经浸提取油后的副产品。'),(181,'紫苏油','油料籽实及其加工产品','酸价\n过氧化值','紫苏籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(182,'氢化脂肪','油料籽实及其加工产品','酸价\n过氧化值','植物油脂经氢化反应获得的产品。产品须由有资质的食品生产企业提供。'),(183,'琉璃苣耔油','油料籽实及其加工产品','酸价\n过氧化值','琉璃苣( Borago officinalis L.)籽经压榨或浸提制取的油。'),(184,'奇亚籽','油料籽实及其加工产品','','唇形科鼠尾草属芡欧鼠尾草（Salvia hispanica L.）的种子'),(185,'大麦次粉','谷物及其加工产品','淀粉\n粗蛋白质\n粗纤维','以大麦为原料经制粉工艺产生的副产品之一，由糊粉层、胚乳及少量细麸组成。'),(186,'大麦蛋白粉','谷物及其加工产品','粗蛋白质','大麦分离出麸皮和淀粉后以蛋白质为主要成分的副产品。'),(187,'大麦粉','谷物及其加工产品','淀粉\n粗蛋白质','大麦经制粉工艺加工形成的以大麦粉为主、含有少量细麦麸和胚的粉状产品。'),(188,'大麦粉浆粉','谷物及其加工产品','粗蛋白质','大麦经湿法加工提取蛋白、淀粉后的液态副产物经浓缩、干燥形成的产品。'),(189,'大麦麸','谷物及其加工产品','粗纤维','以大麦为原料碾磨制粉过程中所分离的麦皮层。'),(190,'大麦壳','谷物及其加工产品','粗纤维','大麦经脱壳工艺除去的外壳。'),(191,'大麦糖渣','谷物及其加工产品','粗蛋白质\n水分','大麦生产淀粉糖的副产品。'),(192,'大麦纤维','谷物及其加工产品','粗纤维','从大麦籽实中提取的纤维，或者生产大麦淀粉过程中提取的纤维类产物。'),(193,'大麦纤维渣','谷物及其加工产品','粗纤维','大麦淀粉加工的副产品，主要成分为纤维素，含有少部分胚乳。'),(194,'大麦皮','谷物及其加工产品','粗纤维','大麦淀粉加工的副产品，主要成分为纤维素，含有少部分胚乳。'),(196,'大麦芽','谷物及其加工产品','粗蛋白质\n粗纤维','大麦发芽后的产品。'),(197,'大麦芽粉','谷物及其加工产品','粗蛋白质\n粗纤维','大麦芽经干燥、碾磨获得的产品。'),(198,'大麦芽根','谷物及其加工产品','粗蛋白质\n粗纤维','发芽大麦或大麦芽清理过程中的副产品，主要由麦芽根、大麦细粉、外皮和碎麦芽组成。'),(199,'烘烤大麦','谷物及其加工产品','淀粉\n粗蛋白质','大麦经适度烘烤形成的产品。'),(200,'喷浆大麦皮','谷物及其加工产品','粗蛋白质\n粗纤维','大麦生产淀粉及胚芽的副产品喷上大麦浸泡液干燥后获得的产品。'),(201,'膨化大麦','谷物及其加工产品','淀粉\n淀粉糊化度','大麦在一定温度和压力条件下经膨化处理获得的产品。'),(202,'全大麦粉','谷物及其加工产品','淀粉\n粗蛋白质','不去除任何皮层的完整大麦籽粒经碾磨获得的产品。'),(203,'压片大麦','谷物及其加工产品','淀粉\n淀粉糊化度','去壳大麦经汽蒸、碾压后的产品。其中可含有少部分大麦壳。可经瘤胃保护。'),(204,'大麦苗粉','谷物及其加工产品','粗蛋白质\n粗纤维\n水分','大麦的幼苗经干燥、粉碎后获得的产品。'),(205,'稻谷','谷物及其加工产品','','禾本科草本植物栽培稻（Oryza sativa L.）的籽实。'),(206,'糙米','谷物及其加工产品','淀粉\n粗纤维','稻谷脱去颖壳后的产品，由皮层、胚乳和胚组成。'),(207,'糙米粉','谷物及其加工产品','淀粉\n粗蛋白质\n粗纤维','糙米经碾磨获得的产品。'),(208,'大米次粉','谷物及其加工产品','淀粉\n粗蛋白质\n粗纤维','由大米加工米粉和淀粉（包含干法和湿法碾磨、过筛）的副产品之一。'),(209,'大米蛋白粉','谷物及其加工产品','粗蛋白质','生产大米淀粉后以蛋白质为主的副产物。由大米经湿法碾磨、筛分、分离、浓缩和干燥获得。'),(210,'大米粉','谷物及其加工产品','淀粉\n粗蛋白质','大米经碾磨获得的产品。'),(211,'大米酶解蛋白','谷物及其加工产品','酸溶蛋白（三氯乙酸可溶蛋白）\n粗蛋白质\n粗灰分\n钙含量','大米蛋白粉经酶水解、干燥后获得的产品。'),(212,'大米抛光次粉','谷物及其加工产品','粗蛋白质\n粗纤维','去除米糠的大米在抛光过程中产生的粉状副产品。'),(213,'大米糖渣','谷物及其加工产品','粗蛋白质\n水分','大米生产淀粉糖的副产品。'),(214,'稻壳粉','谷物及其加工产品','粗纤维','稻谷在砻谷过程中脱去的颖壳经粉碎获得的产品。'),(215,'砻糠粉','谷物及其加工产品','粗纤维','稻谷在砻谷过程中脱去的颖壳经粉碎获得的产品。'),(216,'稻米油','谷物及其加工产品','酸价\n过氧化值','米糠经压榨或浸提制取的油。'),(217,'米糠油','谷物及其加工产品','酸价\n过氧化值','米糠经压榨或浸提制取的油。'),(218,'米糠','谷物及其加工产品','粗脂肪\n酸价\n粗纤维','糙米在碾米过程中分离出的皮层，含有少量胚和胚乳。'),(219,'米糠饼','谷物及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','米糠经压榨取油后的副产品。'),(220,'米糠粕','谷物及其加工产品','粗蛋白质\n粗纤维','米糠或米糠饼经浸提取油后的副产品。'),(221,'脱脂米糠','谷物及其加工产品','粗蛋白质\n粗纤维','米糠或米糠饼经浸提取油后的副产品。'),(222,'膨化大米','谷物及其加工产品','淀粉\n淀粉糊化度','大米或碎米在一定温度和压力条件下，经膨化处理获得的产品。'),(223,'膨化大米粉','谷物及其加工产品','淀粉\n淀粉糊化度','大米或碎米在一定温度和压力条件下，经膨化处理获得的产品。'),(224,'碎米','谷物及其加工产品','淀粉\n粗蛋白质','稻谷加工过程中产生的破碎米粒（含米粞）。'),(225,'统糠','谷物及其加工产品','粗脂肪\n粗纤维\n酸价','稻谷加工过程中自然产生的含有稻壳的米糠，除不可避免的混杂外，不得人为加入稻壳粉。'),(226,'稳定化米糠','谷物及其加工产品','粗脂肪\n粗纤维\n酸价','通过挤压、膨化、微波等稳定化方式灭酶处理过的米糠。'),(227,'压片大米','谷物及其加工产品','淀粉\n淀粉糊化度','预糊化大米经压片获得的产品。'),(228,'预糊化大米','谷物及其加工产品','淀粉\n淀粉糊化度','大米或碎米经湿热、压力等预糊化工艺处理后形成的产品。'),(229,'蒸谷米次粉','谷物及其加工产品','粗蛋白质\n粗纤维\n碳酸钙','经蒸谷处理的去壳糙米粗加工的副产品。主要由种皮、糊粉层、胚乳和胚芽组成，并经碳酸钙处理。'),(230,'大米胚芽','谷物及其加工产品','粗蛋白质\n粗脂肪','大米加工过程中提取的主要含胚芽的产品。'),(231,'大米胚芽粕','谷物及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','大米胚芽经压榨取油后的副产品。'),(232,'高粱','谷物及其加工产品','','高粱（Sorghum bicolor (L.) Moench.）籽实。'),(233,'高粱次粉','谷物及其加工产品','淀粉\n粗纤维','以高梁为原料经制粉工艺产生的副产品之一，由糊粉层、胚乳及少量细麸组成。'),(234,'高粱粉浆粉','谷物及其加工产品','粗蛋白质\n水分','高粱湿法提取蛋白、淀粉后的液态副产物经浓缩、干燥形成的产品。'),(235,'高粱糠','谷物及其加工产品','粗脂肪\n粗纤维','加工高粱米时脱下的皮层、胚和少量胚乳的混合物。'),(236,'高粱米','谷物及其加工产品','淀粉\n粗蛋白质','高粱籽粒经脱皮工艺去除皮层后的产品。'),(237,'去皮高粱粉','谷物及其加工产品','淀粉\n粗蛋白质','高粱籽粒去除种皮、胚芽后，将胚乳部分研磨成适当细度获得的粉状产品。'),(238,'全高粱粉','谷物及其加工产品','淀粉\n粗蛋白质','不去除任何皮层的完整高粱籽粒经碾磨获得的产品。'),(239,'黑麦','谷物及其加工产品','','黑麦（Secale cereale L.）籽实。'),(240,'黑麦次粉','谷物及其加工产品','淀粉\n粗纤维','以黑麦为原料经制粉工艺形成的副产品之一，由糊粉层、胚乳及少量细麸组成。'),(241,'黑麦粉','谷物及其加工产品','淀粉\n粗蛋白质','黑麦经制粉工艺制成的以黑麦粉为主、含有少量细麦麸和胚的粉状产品。'),(242,'黑麦麸','谷物及其加工产品','淀粉\n粗纤维','以黑麦为原料碾磨制粉过程中所分出的麦皮层。'),(243,'全黑麦粉','谷物及其加工产品','淀粉\n粗蛋白质','不去除任何皮层的完整黑麦籽粒经碾磨获得的产品。'),(244,'干黄酒糟','谷物及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','黄酒生产过程中，原料发酵后过滤获得的滤渣经干燥获得的产品。'),(245,'干啤酒糟','谷物及其加工产品','粗蛋白质\n粗脂肪\n粗纤维','以大麦为主要原料生产啤酒的过程中，经糖化工艺后过滤获得的残渣，再经干燥获得的产品。'),(246,'谷物酒糟糖浆','谷物及其加工产品','粗蛋白质\n水分','酿酒生产中谷物发酵蒸馏后的酒糟醪液经蒸发浓缩获得的产品。'),(247,'荞麦次粉','谷物及其加工产品','淀粉\n粗纤维','以荞麦为原料经制粉工艺形成的副产品之一，由糊粉层、胚乳及少量细麸组成。'),(248,'荞麦麸','谷物及其加工产品','淀粉\n粗纤维','荞麦经制粉工艺所分离出的麦皮层。'),(249,'全荞麦粉','谷物及其加工产品','淀粉\n粗蛋白质','以不去除任何皮层的完整荞麦经碾磨获得的产品。'),(250,'黍','谷物及其加工产品','','禾本科草本植物栽培黍（Panicum miliaceum L.）的籽实。'),(251,'黄米','谷物及其加工产品','','禾本科草本植物栽培黍（Panicum miliaceum L.）的籽实。'),(252,'黍米粉','谷物及其加工产品','淀粉\n粗蛋白质','黍米（脱皮或不脱皮）经制粉工艺加工而成的粉状产品。'),(253,'黍米糠','谷物及其加工产品','粗脂肪\n粗纤维\n酸价','黍糙米在碾米过程中分离出的皮层，含有少量胚和胚乳。'),(254,'小米','谷物及其加工产品','淀粉\n粗脂肪','粟经脱皮工艺除去皮层后的部分。按粒质不同分为粳性小米和糯性小米。'),(255,'小米粉','谷物及其加工产品','淀粉\n粗蛋白质','小米经碾磨获得的粉状产品。'),(256,'小米糠','谷物及其加工产品','粗脂肪\n粗纤维','碾米机碾下的糙小米的皮层。'),(257,'全小黑麦粉','谷物及其加工产品','淀粉\n粗蛋白质','以完整小黑麦籽实不去除任何皮层经碾磨获得的产品。'),(258,'小黑麦次粉','谷物及其加工产品','淀粉\n粗纤维','以小黑麦为原料经制粉工艺形成的的副产品之一。由糊粉层、胚乳及少量细麸组成。'),(259,'小黑麦粉','谷物及其加工产品','淀粉\n粗蛋白质','小黑麦经制粉工艺制成的以小黑麦粉为主、含有少量细麦麸和胚的粉状产品。'),(260,'小黑麦麸','谷物及其加工产品','淀粉\n粗纤维','以小黑麦为原料碾磨制粉过程中所分出的麦皮层。'),(261,'小麦','谷物及其加工产品','','小麦（Triticum aestivum L.）的籽实。可经瘤胃保护。'),(262,'发芽小麦[芽麦]','谷物及其加工产品','粗蛋白质\n粗纤维','发芽的小麦。'),(263,'辣椒','其它籽实、果实类产品及其加工产品','粗蛋白\n粗灰分','辣椒（Capsicum annuum L.）经干燥、粉碎后所得的产品。'),(264,'辣椒粉','其它籽实、果实类产品及其加工产品','粗蛋白\n粗灰分','辣椒（Capsicum annuum L.）经干燥、粉碎后所得的产品。'),(265,'辣椒渣','其它籽实、果实类产品及其加工产品','粗蛋白质\n粗灰分','辣椒皮提取红色素后的副产品。'),(266,'辣椒籽粕','其它籽实、果实类产品及其加工产品','粗蛋白质\n粗纤维','辣椒籽取油后的副产品。'),(267,'辣椒籽油','其它籽实、果实类产品及其加工产品','酸价、过氧化值。','辣椒籽经压榨或浸提制取的油。产品须由有资质的食品生产企业提供。'),(268,'鳄梨浓缩汁','其它籽实、果实类产品及其加工产品','总糖\n水分','鳄梨压榨后的汁液经浓缩后获得的产品。产品须由有资质的食品生产企业提供。'),(269,'牛油果浓缩汁','其它籽实、果实类产品及其加工产品','总糖\n水分','鳄梨压榨后的汁液经浓缩后获得的产品。产品须由有资质的食品生产企业提供。'),(270,'果仁','其它籽实、果实类产品及其加工产品','粗蛋白质\n粗脂肪','可食用的坚果仁或水果仁。'),(271,'果渣','其它籽实、果实类产品及其加工产品','粗纤维\n粗灰分\n水分','可食用水果榨汁或果品加工过程中获得的副产品，'),(272,'枣','其它籽实、果实类产品及其加工产品','','食用枣（Ziziphus jujuba Mill.）。'),(273,'枣粉','其它籽实、果实类产品及其加工产品','粗纤维\n粗灰分','食用枣经干燥、粉碎获得的产品。'),(274,'果汁','其它籽实、果实类产品及其加工产品','总糖\n水分','可食用水果鲜果,或对其进行加工后获得的果汁、果泥、果片、果干、果粉等。不得使用变质原料。'),(275,'果泥','其它籽实、果实类产品及其加工产品','总糖\n水分','可食用水果鲜果,或对其进行加工后获得的果汁、果泥、果片、果干、果粉等。不得使用变质原料。'),(276,'果片','其它籽实、果实类产品及其加工产品','总糖\n水分','可食用水果鲜果,或对其进行加工后获得的果汁、果泥、果片、果干、果粉等。不得使用变质原料。'),(277,'果干','其它籽实、果实类产品及其加工产品','总糖\n水分','可食用水果鲜果,或对其进行加工后获得的果汁、果泥、果片、果干、果粉等。不得使用变质原料。'),(278,'果粉','其它籽实、果实类产品及其加工产品','总糖\n水分','可食用水果鲜果,或对其进行加工后获得的果汁、果泥、果片、果干、果粉等。不得使用变质原料。'),(279,'苜蓿渣','饲草、粗饲料及其加工产品','粗蛋白质\n中性洗涤纤维','苜蓿干草粉用水提取苜蓿多糖等成分后获得的副产品。可经烘干、粉碎或挤压成颗粒状。'),(280,'秸秆','饲草、粗饲料及其加工产品','粗灰分\n中性洗涤纤维','成熟农作物干的茎叶（穗）。产品名称应标明作物的品种，如：玉米秸秆。'),(281,'辣木茎叶','饲草、粗饲料及其加工产品','粗蛋白质\n中性洗涤纤维\n水分','辣木（Moringa）可饲用品种的新鲜或干燥茎叶。'),(282,'甘蔗渣','其它植物、藻类及其加工产品','粗纤维\n水分','甘蔗提取糖后剩余的植物部分，主要由纤维组成。'),(283,'蔗糖','其它植物、藻类及其加工产品','','见13.4.1和13.4.3'),(284,'丝兰粉','其它植物、藻类及其加工产品','吸氨量\n水分','丝兰（Yucca schidigera Roezl.）干燥、粉碎后得到的粉状产品。'),(285,'丝兰','其它植物、藻类及其加工产品','粗纤维\n水分','百合科丝兰属丝兰( Yucca schidigera RoezL.) 。'),(286,'丝兰汁','其它植物、藻类及其加工产品','','丝兰压榨后的汁液,或汁液经浓缩后获得的产品。'),(287,'万寿菊渣','其它植物、藻类及其加工产品','粗蛋白质\n粗纤维\n粗灰分\n水分','万寿菊（Tagetes erecta L.）提取叶黄素后的副产品。'),(288,'万寿菊粉','其它植物、藻类及其加工产品','粗纤维\n粗灰分\n叶黄素','万寿菊干燥、粉碎后得到的粉状产物。'),(289,'藻渣','其它植物、藻类及其加工产品','总糖\n粗灰分\n水分','可食用大型海藻经提取活性成分后的副产品，产品名称应标明使用原料的来源，如：海带渣。'),(290,'螺旋藻粉','其它植物、藻类及其加工产品','粗蛋白质\n粗灰分','螺旋藻（Spirulina platensis）干燥、粉碎后的产品。'),(291,'微藻粕','其它植物、藻类及其加工产品','粗蛋白\n粗灰分','裂壶藻粉、拟微绿球藻粉或小球藻粉浸提脂肪后，经干燥得到的副产品。'),(292,'裸藻','其它植物、藻类及其加工产品','','裸藻（Euglena)及其干燥产品.'),(293,'绿虫藻','其它植物、藻类及其加工产品','','裸藻（Euglena)及其干燥产品.'),(294,'藻油','其它植物、藻类及其加工产品','粗脂肪\n酸价\n过氧化值','本目录所列的藻类经压榨或浸提制取的油。产品名称应标明原料来源。如裂壶藻油。'),(295,'八角茴香','其它植物、藻类及其加工产品','','木兰科八角属植物八角(Illicium verum Hook.)的干燥成熟果实。'),(296,'白扁豆','其它植物、藻类及其加工产品','','豆科扁豆属(Lablab Adans.) 植物的干燥成熟种子。'),(297,'白芍','其它植物、藻类及其加工产品','','毛茛科芍药亚科芍药属植物芍药(Paeonia lactiflora Pall.)的干燥根。'),(298,'薄荷','其它植物、藻类及其加工产品','','唇形科薄荷属植物薄荷（Mentha haplocalyx Briq.）的干燥地上部分。'),(299,'补骨脂','其它植物、藻类及其加工产品','','豆科补骨脂属植物补骨脂(Psoralea corylifolia L.)的干燥成熟果实。'),(300,'川芎','其它植物、藻类及其加工产品','','伞形科藁本属植物川芎(Ligusticum chuanxiong Hort.)的干燥根茎。'),(301,'淡豆豉','其它植物、藻类及其加工产品','','豆科大豆属植物大豆(Glycine max (L.) Merr.)的成熟种子的发酵加工品。'),(302,'杜仲','其它植物、藻类及其加工产品','','杜仲科杜仲属植物杜仲(Eucommia ulmoides Oliv.)的干燥树皮。'),(303,'杜仲叶','其它植物、藻类及其加工产品','','杜仲科杜仲属植物杜仲(Eucommia ulmoides Oliv.)的干燥叶。'),(304,'榧子','其它植物、藻类及其加工产品','','红豆杉科榧树属植物榧树(Torreya grandis Fort.)的干燥成熟种子。'),(305,'茯苓','其它植物、藻类及其加工产品','','多孔菌科茯苓属真菌茯苓(Poria cocos (Schw.) Wolf)的干燥菌核。'),(306,'干姜','其它植物、藻类及其加工产品','','姜科姜属植物姜(Zingiber officinale Rosc.)的干燥根茎。'),(307,'高良姜','其它植物、藻类及其加工产品','','姜科山姜属植物高良姜(Alpinia officinarum Hance)的干燥根茎。'),(308,'葛根','其它植物、藻类及其加工产品','','豆科葛属植物葛(Pueraria lobata (Willd.) Ohwi)的干燥根。'),(309,'荷叶','其它植物、藻类及其加工产品','','睡莲科莲亚科莲属植物莲(Nelumbo nucifera Gaertn.)的干燥叶。'),(310,'黑芝麻','其它植物、藻类及其加工产品','','胡麻科胡麻属植物芝麻（Sesamum indicum L.）的干燥成熟种子。'),(311,'胡芦巴','其它植物、藻类及其加工产品','','豆科植物胡芦巴(Trigonella foenum-graecum L.)的干燥成熟种子。'),(312,'槐角','其它植物、藻类及其加工产品','','豆科槐属植物槐(Sophora japonica L.)的干燥成熟果实。'),(313,'槐实','其它植物、藻类及其加工产品','','豆科槐属植物槐(Sophora japonica L.)的干燥成熟果实。'),(314,'姜黄','其它植物、藻类及其加工产品','','姜科姜黄属植物姜黄(Curcuma longa L.)的干燥根茎。'),(315,'绞股蓝','其它植物、藻类及其加工产品','','葫芦科绞股蓝属（Gynostemma Bl.）植物。'),(316,'金樱子','其它植物、藻类及其加工产品','','蔷薇科蔷薇属植物金樱子(Rosa laevigata Michx.)的干燥成熟果实。'),(317,'决明子','其它植物、藻类及其加工产品','','豆科决明属植物决明(Cassia tora L.)的干燥成熟种子。'),(318,'莱菔子','其它植物、藻类及其加工产品','','十字花科萝卜属植物萝卜(Raphanus sativus L.)的干燥成熟种子。'),(319,'莲子','其它植物、藻类及其加工产品','','睡莲科莲亚科莲属植物莲（Nelumbo nucifera Gaertn.）的干燥成熟种子。'),(320,'马齿苋','其它植物、藻类及其加工产品','','马齿苋科马齿苋属植物马齿苋(Portulaca oleracea L.)的干燥地上部分。'),(321,'玫瑰花','其它植物、藻类及其加工产品','','蔷薇科蔷薇属植物玫瑰(Rosa rugosa Thunb.)的干燥花蕾。'),(322,'牛蒡子','其它植物、藻类及其加工产品','','菊科牛蒡属植物牛蒡(Arctium lappa L.)的干燥成熟果实。'),(323,'女贞子','其它植物、藻类及其加工产品','','木犀科女贞属植物女贞(Ligustrum lucidum Ait.)的干燥成熟果实。'),(324,'茜草','其它植物、藻类及其加工产品','','茜草科茜草属植物茜草(Rubia cordifolia L.)的干燥根及根茎。'),(325,'人参','其它植物、藻类及其加工产品','','五加科人参属植物人参(Panax ginseng C. A. Mey.)的干燥根及根茎。'),(326,'人参叶','其它植物、藻类及其加工产品','','五加科人参属植物人参(Panax ginseng C. A. Mey.)的干燥叶。'),(327,'桑白皮','其它植物、藻类及其加工产品','','桑科桑属植物桑(Morus alba L.)的干燥根皮。'),(328,'桑椹','其它植物、藻类及其加工产品','','桑科桑属植物桑(Morus alba L.)的干燥果穗。'),(329,'桑叶','其它植物、藻类及其加工产品','','桑科桑属植物桑(Morus alba L.)的干燥叶。'),(330,'桑枝','其它植物、藻类及其加工产品','','桑科桑属植物桑(Morus alba L.)的干燥嫩枝。'),(331,'沙棘','其它植物、藻类及其加工产品','','胡颓子科沙棘属植物沙棘(Hippophae rhamnoides L.)的干燥成熟果实。'),(332,'山药','其它植物、藻类及其加工产品','','薯蓣科薯蓣属植物薯蓣(Dioscorea opposita Thunb.)的干燥根茎。'),(333,'生姜','其它植物、藻类及其加工产品','','姜科姜属植物姜(Zingiber officinale Rosc.)的新鲜根茎。'),(334,'酸角','其它植物、藻类及其加工产品','','豆科酸豆属植物酸豆(Tamarindus indica L.)的果实。'),(335,'土茯苓','其它植物、藻类及其加工产品','','百合科菝葜属植物土茯苓(Smilax glabra Roxb.)的干燥根茎。'),(336,'乌梅','其它植物、藻类及其加工产品','','蔷薇科杏属植物梅(Armeniaca mume Sieb.)的干燥近成熟果实。'),(337,'香附','其它植物、藻类及其加工产品','','莎草科莎草属植物香附子(Cyperus rotundus L.)的干燥根茎。'),(338,'洋槐花','其它植物、藻类及其加工产品','','豆科刺槐属植物刺槐(Robinia pseudoacacia L.)的花，可经干燥、粉碎。'),(339,'杨树花','其它植物、藻类及其加工产品','','杨柳科杨属(Populus L.)植物的花，可经干燥、粉碎。'),(340,'野菊花','其它植物、藻类及其加工产品','','菊科菊属植物野菊(Dendranthema indicum L.)的干燥头状花序。'),(341,'薏苡仁','其它植物、藻类及其加工产品','','禾本科薏苡属植物薏苡(Coix lacryma-jobi L.)的干燥成熟种仁。'),(342,'益智','其它植物、藻类及其加工产品','','姜科山姜属植物益智(Alpinia oxyphylla Miq.)的干燥成熟果实。'),(343,'益智仁','其它植物、藻类及其加工产品','','姜科山姜属植物益智(Alpinia oxyphylla Miq.)的干燥成熟果实。'),(344,'银杏叶','其它植物、藻类及其加工产品','','银杏科银杏属植物银杏(Ginkgo biloba L.)的干燥叶。'),(345,'越橘','其它植物、藻类及其加工产品','','杜鹃花科越橘属(Vaccinium L.)植物的果实或叶。'),(346,'绿茶','其它植物、藻类及其加工产品','','以茶树的新叶或芽为原料，未经发酵。经杀青、整形、烘干等工序制成的产品。'),(347,'迷迭香','其它植物、藻类及其加工产品','','唇形科迷迭香属植物迷迭香(Rosmarinus officinalis）的干燥茎叶或花。'),(348,'乳清粉','乳制品及其副产品','蛋白质\n粗灰分\n乳糖','以乳清为原料经干燥制成的粉末状产品。产品须由有资质的乳制品生产企业提供。'),(349,'分离乳清蛋白','乳制品及其副产品','蛋白质\n粗灰分','乳清蛋白粉的一种，蛋白质含量不低于90%。产品须由有资质的乳制品生产企业提供。'),(350,'浓缩乳清蛋白','乳制品及其副产品','蛋白质\n粗灰分\n乳糖','乳清蛋白粉的一种，蛋白质含量不低于34%。产品须由有资质的乳制品生产企业提供。'),(351,'乳钙','乳制品及其副产品','钙\n磷\n粗灰分','从乳清液中分离出的高钙含量的产品。钙含量不低于22%。产品须由有资质的乳制品生产企业提供。'),(352,'乳矿物盐','乳制品及其副产品','钙\n磷\n粗灰分','从乳清液中分离出的高钙含量的产品。钙含量不低于22%。产品须由有资质的乳制品生产企业提供。'),(353,'蚕蛹','陆生动物产品及其副产品','粗蛋白质\n粗脂肪\n酸价','蚕蛹经干燥获得的产品。可将其粉碎。'),(354,'蚕蛹粉','陆生动物产品及其副产品','粗蛋白质\n粗脂肪\n酸价','蚕蛹经干燥获得的产品。可将其粉碎。'),(355,'脱脂蚕蛹粉','陆生动物产品及其副产品','粗蛋白质\n粗脂肪\n酸价','蚕蛹（粉）脱脂处理后获得的产品。'),(356,'脱脂蚕蛹','陆生动物产品及其副产品','粗蛋白质\n粗脂肪\n酸价','蚕蛹（粉）脱脂处理后获得的产品。'),(357,'蚕蛹粕','陆生动物产品及其副产品','粗蛋白质\n粗脂肪\n酸价','蚕蛹（粉）脱脂处理后获得的产品。'),(358,'蜂蜜','陆生动物产品及其副产品','总糖','蜜蜂科昆虫中华蜜蜂或意大利蜂所酿的蜜，可进行适当加工。产品须由有资质的食品生产企业提供。'),(359,'膨化羽毛粉','陆生动物产品及其副产品','粗蛋白质\n粗灰分\n胃蛋白酶消化率','家禽羽毛经膨化、粉碎后获得的产品。原料不得使用发生疫病和变质家禽羽毛。'),(360,'蛋粉','陆生动物产品及其副产品','粗蛋白质\n粗灰分','食用鲜蛋的蛋液，经巴氏消毒、干燥、脱水获得的产品。产品不含蛋壳或其它非蛋原料。'),(361,'蛋黄粉','陆生动物产品及其副产品','粗蛋白质\n粗脂肪','食用鲜蛋的蛋黄，经巴氏消毒、干燥、脱水获得的产品。产品不含蛋壳或其它非蛋原料。'),(362,'蛋壳粉','陆生动物产品及其副产品','粗灰分\n钙','禽蛋壳经灭菌、干燥、粉碎获得的产品。'),(363,'蛋清粉','陆生动物产品及其副产品','粗蛋白质','食用鲜蛋的蛋清，经巴氏消毒、干燥、脱水获得的产品。产品不含蛋壳或其它非蛋原料。'),(364,'蚯蚓粉','陆生动物产品及其副产品','粗蛋白质\n粗灰分','蚯蚓经干燥、粉碎的产品。'),(365,'骨胶','陆生动物产品及其副产品','凝胶强度\n勃氏粘度\n粗灰分','可食用动物骨骼经轧碎、脱油、水解获得的蛋白类产品。原料不得使用发生疫病和变质的动物骨骼。'),(366,'脱胶骨粉','陆生动物产品及其副产品','粗灰分\n总磷\n钙','食用动物骨骼经脱胶、干燥、粉碎获得的产品。原料不得使用发生疫病和变质的动物骨骼。'),(367,'凹凸棒石','矿物质','镁\n水分','天然水合镁铝硅酸盐矿物，可以是粒状或经粉碎后的粉。'),(368,'凹凸棒石粉','矿物质','镁\n水分','天然水合镁铝硅酸盐矿物，可以是粒状或经粉碎后的粉。'),(369,'沸石粉','矿物质','钙\n吸蓝量\n吸氨值\n水分','天然斜发沸石或丝光沸石经粉碎获得的产品。'),(370,'海泡石','矿物质','水分','一种水合富镁硅酸盐黏土矿物。'),(371,'滑石粉','矿物质','水分','天然硅酸镁盐类矿物滑石经精选、净化、粉碎、干燥获得的产品。'),(372,'麦饭石','矿物质','水分','天然的无机硅铝酸盐。'),(373,'膨润土','矿物质','水分','以蒙脱石为主要成分的粘土岩—蒙脱石粘土岩。'),(374,'斑脱岩','矿物质','水分','以蒙脱石为主要成分的粘土岩—蒙脱石粘土岩。'),(375,'膨土岩','矿物质','水分','以蒙脱石为主要成分的粘土岩—蒙脱石粘土岩。'),(376,'蛭石','矿物质','水分\n氟','含有硅酸镁、铝、铁的天然矿物质经加热膨胀形成的产品。不得含有石棉。'),(377,'贝壳粉','鱼、其它水生生物及其副产品','粗灰分\n钙','贝类的壳经过干燥、粉碎获得的产品。'),(378,'干贝粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n组胺','食品企业加工食用干贝（扇贝柱）剩余的边角料（不包括壳），经干燥、粉碎获得的产品。'),(379,'虾','鱼、其它水生生物及其副产品','','新鲜的虾。可以鲜用或根据使用要求对其进行冷藏、冷冻、蒸煮、干燥处理。'),(380,'磷虾粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗灰分\n盐分\n挥发性盐基氮','以磷虾（Euphausia superba）为原料，经干燥、粉碎获得的产品。'),(381,'虾粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗灰分\n盐分\n挥发性盐基氮','虾经蒸煮、干燥、粉碎获得的产品。'),(382,'虾膏','鱼、其它水生生物及其副产品','粗蛋白质\n粗灰分\n水分\n挥发性盐基氮','以虾为原料，经油脂分离、酶解、浓缩获得的膏状物。'),(383,'虾壳粉','鱼、其它水生生物及其副产品','粗灰分','以食品企业加工虾仁过程中剥离出的虾头、虾壳为原料，经干燥、粉碎获得的产品。'),(384,'虾油','鱼、其它水生生物及其副产品','脂肪\n酸价\n碘价','以海洋虾类经蒸煮、压榨、分离获得的毛油为原料，再进行精炼获得的产品。'),(385,'蟹','鱼、其它水生生物及其副产品','','新鲜的蟹。可以鲜用或根据使用要求对其进行冷藏、冷冻、蒸煮、干燥处理。'),(386,'蟹壳粉','鱼、其它水生生物及其副产品','粗灰分','以蟹壳为原料，经烘干、粉碎获得的产品。'),(387,'乌贼','鱼、其它水生生物及其副产品','','新鲜的乌贼。可以鲜用或根据使用要求对其进行冷藏、冷冻、蒸煮、干燥处理。'),(388,'乌贼粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n粗灰分\n挥发性盐基氮','乌贼经蒸煮、压榨、干燥、粉碎获得的产品。'),(389,'乌贼膏','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n粗灰分\n挥发性盐基氮\n水分','以乌贼内脏为原料，经油脂分离、酶解、浓缩获得的膏状物。'),(390,'乌贼油','鱼、其它水生生物及其副产品','粗脂肪\n酸价\n碘价','从乌贼内脏中分离出的油脂。'),(391,'鱿鱼','鱼、其它水生生物及其副产品','粗脂肪\n酸价','新鲜的鱿鱼。可以鲜用根据使用要求可对其进行冷藏、冷冻、蒸煮或干燥处理。'),(392,'鱿鱼粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n挥发性盐基氮','鱿鱼经蒸煮、压榨、干燥、粉碎获得的产品。'),(393,'鱿鱼膏','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n粗灰分\n挥发性盐基氮\n水分','以鱿鱼内脏为原料，经油脂分离、酶解、浓缩获得的膏状物。'),(394,'鱿鱼油','鱼、其它水生生物及其副产品','粗脂肪\n酸价\n碘价','从鱿鱼内脏中分离出的油脂。'),(395,'水解鱼蛋白粉','鱼、其它水生生物及其副产品','粗蛋白质\n粗脂肪\n粗灰分','以全鱼或鱼的某一部分为原料，经浓缩、水解、干燥获得的产品。产品中粗蛋白质含量不低于50%。'),(396,'鱼膏','鱼、其它水生生物及其副产品','粗蛋白质\n粗灰分\n挥发性盐基氮\n水分','以鲜鱼内脏等下杂物为原料，经油脂分离、酶解、浓缩获得的膏状物。'),(397,'鱼骨粉','鱼、其它水生生物及其副产品','钙\n磷\n粗灰分','鱼类的骨骼经粉碎、烘干获得的产品。'),(398,'鱼油','鱼、其它水生生物及其副产品','粗脂肪\n酸价\n碘价\n丙二醛','对全鱼或鱼的某一部分经蒸煮、压榨获得的毛油，再进行精炼获得的产品。'),(399,'鱼皮','鱼、其它水生生物及其副产品','粗蛋白质\n水分','加工鱼类产品过程中获得的鱼皮经干燥后的产品。'),(400,'卤虫卵','鱼、其它水生生物及其副产品','空壳率\n孵化率','卤虫及其卵。'),(409,'鸡肉粉','动物加工副产品及其加工产品','AAFCO定义，浓缩动物蛋白源，品质差异大','鸡肉粉是由屠宰后洁净的整只鸡或鸡肉组织部分（通常包括肌肉、皮肤和附着的骨头），经蒸煮、压榨脱脂、干燥和粉碎后制成的浓缩动物蛋白饲料原料。根据AAFCO标准，优质鸡肉粉不应含有羽毛、头、脚、爪、内脏内容物等。在猫粮应用中，它是一种高效、稳定的蛋白质和必需氨基酸（如牛磺酸）来源，同时天然提供猫所需的钙、磷等矿物质。其低水分特性使其在干粮配方中能提供比等重鲜鸡肉更大量的蛋白质。然而，鸡肉粉的品质至关重要：高品质鸡肉粉（通常灰分含量<12%，蛋白质消化率高）是优质猫粮的核心成分；而低品质鸡肉粉可能来源不明、灰分过高或已氧化变质，营养价值远逊于鲜鸡肉。消费者应选择信誉良好的品牌，并关注成分表中肉类原料的整体构成，而非单一贬低或推崇肉粉。');
/*!40000 ALTER TABLE `ingredient` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-30 19:11:46
