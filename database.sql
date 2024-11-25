drop table if exists urls cascade;
drop table if exists url_checks cascade;

create table urls (
id int primary key generated always as identity,
name varchar(255) unique not null,
created_at date not null
);

create table url_checks (
    id int primary key generated always as identity,
    url_id int references urls (id) not null,
    status_code int,
    h1 text,
    title text,
    description text,
    created_at date not null
);