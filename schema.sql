drop table if exists photos;
create table photos (
       id integer primary key autoincrement,
       display_position integer,
       filename text,
       category text
);
