drop table if exists items;
create table items (
  id integer primary key autoincrement,
  title text not null,
  description text null,
  family text not null,
  genus text not null,
  post_date timestamp,
  inactive_date date null
);
drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null unique,
  password text not null
);
drop table if exists likes;
create table likes (
  id integer primary key autoincrement,
  likes  integer not null
);