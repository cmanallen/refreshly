drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  description text null,
  type text null,
  family text null,
  genus text null
);
drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null unique,
  password text not null
);