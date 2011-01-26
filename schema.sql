drop table if exists photo;
drop table if exists category;

create table photo (
       photoid integer primary key autoincrement,
       photodisplayposition integer,
       photofilename text,
       photocategory int,
       foreign key(photocategory) references category(categoryid)
);

create table category (
       categoryid integer primary key autoincrement,
       categoryname text
);

-- initial categories
insert into category (categoryname) values ("landscape");
insert into category (categoryname) values ("personal");
insert into category (categoryname) values ("portrait");
