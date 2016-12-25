-- phpMyAdmin SQL Dump
-- version 4.6.5.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 25, 2016 at 12:46 PM
-- Server version: 10.1.20-MariaDB-1~trusty
-- PHP Version: 5.6.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `discord`
--

-- --------------------------------------------------------

--
-- Table structure for table `afk`
--

CREATE TABLE `afk` (
  `user` bigint(20) NOT NULL,
  `reason` text,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `banned_nsfw_tags`
--

CREATE TABLE `banned_nsfw_tags` (
  `server` bigint(20) NOT NULL,
  `tag` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist`
--

CREATE TABLE `blacklist` (
  `server` bigint(20) NOT NULL,
  `user` bigint(20) NOT NULL,
  `admin` bigint(20) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `channel_blacklist`
--

CREATE TABLE `channel_blacklist` (
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `admin` bigint(20) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `command_blacklist`
--

CREATE TABLE `command_blacklist` (
  `command` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `server` bigint(20) DEFAULT NULL,
  `user` bigint(20) DEFAULT NULL,
  `role` bigint(20) DEFAULT NULL,
  `channel` bigint(20) DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `command_delete`
--

CREATE TABLE `command_delete` (
  `server` bigint(20) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `command_logs`
--

CREATE TABLE `command_logs` (
  `shard` smallint(6) DEFAULT NULL,
  `server` bigint(20) DEFAULT NULL,
  `server_name` varchar(127) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel` bigint(20) DEFAULT NULL,
  `channel_name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user` varchar(48) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `command` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_id` bigint(20) NOT NULL,
  `attachment` text COLLATE utf8mb4_unicode_ci,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `shard` int(11) NOT NULL,
  `user` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `global_blacklist`
--

CREATE TABLE `global_blacklist` (
  `user` bigint(20) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `global_log_ignore`
--

CREATE TABLE `global_log_ignore` (
  `user` bigint(20) NOT NULL,
  `avatar` tinyint(1) NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `google_nsfw`
--

CREATE TABLE `google_nsfw` (
  `server` bigint(20) NOT NULL,
  `level` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `leave`
--

CREATE TABLE `leave` (
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci,
  `user` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `logs`
--

CREATE TABLE `logs` (
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `ignore_users` text,
  `avatar_ignore` text,
  `id` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `shard` int(11) DEFAULT NULL,
  `server` bigint(20) DEFAULT NULL,
  `server_name` varchar(127) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel` bigint(20) DEFAULT NULL,
  `channel_name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_after` text COLLATE utf8mb4_unicode_ci,
  `message_id` bigint(20) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `attachment` text COLLATE utf8mb4_unicode_ci,
  `action` smallint(6) NOT NULL,
  `messages_id` bigint(20) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `muted`
--

CREATE TABLE `muted` (
  `server` bigint(20) NOT NULL,
  `user` bigint(20) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `names`
--

CREATE TABLE `names` (
  `id` text NOT NULL,
  `name` text NOT NULL,
  `nickname` text NOT NULL,
  `time` text NOT NULL,
  `server` text NOT NULL,
  `discrim` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `pager`
--

CREATE TABLE `pager` (
  `server` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `text` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `pager_settings`
--

CREATE TABLE `pager_settings` (
  `server` text NOT NULL,
  `id` text NOT NULL,
  `method` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `prefix`
--

CREATE TABLE `prefix` (
  `server` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `prefix` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `prefix_channel`
--

CREATE TABLE `prefix_channel` (
  `server` text NOT NULL,
  `channel` text NOT NULL,
  `prefix` text NOT NULL,
  `id` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ratings`
--

CREATE TABLE `ratings` (
  `server` bigint(20) NOT NULL,
  `user` bigint(20) NOT NULL,
  `rating` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reminders`
--

CREATE TABLE `reminders` (
  `id` int(11) NOT NULL,
  `user` bigint(20) NOT NULL,
  `time` bigint(20) NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci,
  `current` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `server_names`
--

CREATE TABLE `server_names` (
  `id` text NOT NULL,
  `name` text NOT NULL,
  `time` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `stats`
--

CREATE TABLE `stats` (
  `shard` smallint(6) NOT NULL,
  `servers` bigint(20) NOT NULL,
  `largest_member_server` bigint(20) NOT NULL,
  `largest_member_server_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `users` bigint(20) NOT NULL,
  `unique_users` bigint(20) NOT NULL,
  `text_channels` int(11) NOT NULL,
  `voice_channels` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tags`
--

CREATE TABLE `tags` (
  `server` bigint(20) DEFAULT NULL,
  `user` bigint(20) NOT NULL,
  `tag` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_created` bigint(20) DEFAULT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- --------------------------------------------------------

--
-- Table structure for table `tracking`
--

CREATE TABLE `tracking` (
  `txt` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `verification`
--

CREATE TABLE `verification` (
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `mentions` text COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `verification_queue`
--

CREATE TABLE `verification_queue` (
  `user` bigint(20) NOT NULL,
  `server` bigint(20) NOT NULL,
  `id` mediumint(9) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `verification_steam`
--

CREATE TABLE `verification_steam` (
  `user` bigint(20) NOT NULL,
  `server` bigint(20) NOT NULL,
  `steam` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `welcome`
--

CREATE TABLE `welcome` (
  `server` bigint(20) NOT NULL,
  `channel` bigint(20) NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci,
  `user` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `afk`
--
ALTER TABLE `afk`
  ADD UNIQUE KEY `user` (`user`);

--
-- Indexes for table `blacklist`
--
ALTER TABLE `blacklist`
  ADD KEY `id` (`id`);

--
-- Indexes for table `channel_blacklist`
--
ALTER TABLE `channel_blacklist`
  ADD KEY `id` (`id`);

--
-- Indexes for table `command_blacklist`
--
ALTER TABLE `command_blacklist`
  ADD KEY `id` (`id`);

--
-- Indexes for table `command_delete`
--
ALTER TABLE `command_delete`
  ADD PRIMARY KEY (`id`),
  ADD KEY `server` (`server`);

--
-- Indexes for table `command_logs`
--
ALTER TABLE `command_logs`
  ADD PRIMARY KEY (`message_id`) USING BTREE,
  ADD KEY `server_index` (`server`),
  ADD KEY `message_id_index` (`message_id`) USING BTREE,
  ADD KEY `command_index` (`command`),
  ADD KEY `user_id_index` (`user_id`),
  ADD KEY `channel_index` (`channel`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `global_log_ignore`
--
ALTER TABLE `global_log_ignore`
  ADD PRIMARY KEY (`user`),
  ADD KEY `user_index` (`user`) USING BTREE,
  ADD KEY `avatar` (`avatar`);

--
-- Indexes for table `google_nsfw`
--
ALTER TABLE `google_nsfw`
  ADD PRIMARY KEY (`server`);

--
-- Indexes for table `leave`
--
ALTER TABLE `leave`
  ADD UNIQUE KEY `server` (`server`);

--
-- Indexes for table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id` (`id`),
  ADD KEY `server_index` (`server`),
  ADD KEY `channel_index` (`channel`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`messages_id`),
  ADD KEY `messages_id` (`messages_id`) USING BTREE,
  ADD KEY `server_index` (`server`),
  ADD KEY `user_id_index` (`user_id`),
  ADD KEY `channel_index` (`channel`),
  ADD KEY `action_index` (`action`);

--
-- Indexes for table `muted`
--
ALTER TABLE `muted`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id` (`id`);

--
-- Indexes for table `reminders`
--
ALTER TABLE `reminders`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `stats`
--
ALTER TABLE `stats`
  ADD PRIMARY KEY (`shard`);

--
-- Indexes for table `tags`
--
ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tracking`
--
ALTER TABLE `tracking`
  ADD KEY `id` (`id`),
  ADD KEY `server_index` (`server`),
  ADD KEY `channel_index` (`channel`);

--
-- Indexes for table `verification`
--
ALTER TABLE `verification`
  ADD UNIQUE KEY `server` (`server`);

--
-- Indexes for table `welcome`
--
ALTER TABLE `welcome`
  ADD UNIQUE KEY `server` (`server`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `blacklist`
--
ALTER TABLE `blacklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;
--
-- AUTO_INCREMENT for table `channel_blacklist`
--
ALTER TABLE `channel_blacklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=126;
--
-- AUTO_INCREMENT for table `command_blacklist`
--
ALTER TABLE `command_blacklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1940;
--
-- AUTO_INCREMENT for table `command_delete`
--
ALTER TABLE `command_delete`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1105;
--
-- AUTO_INCREMENT for table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=402;
--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `messages_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66510920;
--
-- AUTO_INCREMENT for table `muted`
--
ALTER TABLE `muted`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=467;
--
-- AUTO_INCREMENT for table `reminders`
--
ALTER TABLE `reminders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=389;
--
-- AUTO_INCREMENT for table `tags`
--
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2678;
--
-- AUTO_INCREMENT for table `tracking`
--
ALTER TABLE `tracking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=274;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
