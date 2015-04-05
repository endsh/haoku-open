/* 网站表 */
CREATE TABLE IF NOT EXISTS site (
	`id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	`name` varchar(100) NOT NULL DEFAULT '' COMMENT '网站名称',
	`domain` varchar(100) NOT NULL DEFAULT '' COMMENT '网站域名',
	`addtime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '添加时间',
	`uptime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '更新时间',
	PRIMARY KEY (`id`),
	KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

/* url表 */
CREATE TABLE IF NOT EXISTS url (
	`id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	`url` varchar(256) NOT NULL DEFAULT '' COMMENT 'url地址',
	`rss_count` int(10) unsigned NOT NULL DEFAULT 0 COMMENT '抓到的rss数',
	`addtime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '添加时间',
	`uptime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '更新时间',
	PRIMARY KEY (`id`),
	KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

/* rss表 */
CREATE TABLE IF NOT EXISTS rss (
	`id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	`url` varchar(256) NOT NULL DEFAULT '' COMMENT 'url地址',
	`count` int(10) unsigned NOT NULL DEFAULT 0 COMMENT '累计更新次数',
	`article_count` int(10) unsigned NOT NULL DEFAULT 0 COMMENT '累计更新文章数',
	`invalid_count` int(10) unsigned NOT NULL DEFAULT 0 COMMENT '累计更新失败次数',
	`addtime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '添加时间',
	`uptime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '更新时间',
	PRIMARY KEY (`id`),
	KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
