drop table if exists photos;
create table photos (
       id integer primary key autoincrement,
       filename text,
       category text
);
