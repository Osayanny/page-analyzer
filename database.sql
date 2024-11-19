drop table if exists urls;

create table Urls (
id int primary key generated always as identity,
name varchar(255) unique not null,
created_at date not null
);