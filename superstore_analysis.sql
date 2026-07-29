-- superstore sales analysis
-- dataset: Sample Superstore (kaggle) - 9994 rows
-- tool: MySQL 8


create database if not exists superstore_db;
use superstore_db;


-- create the main table
drop table if exists orders;

create table orders (
    row_id        int,
    order_id      varchar(20),
    order_date    date,
    ship_date     date,
    ship_mode     varchar(30),
    customer_id   varchar(20),
    customer_name varchar(60),
    segment       varchar(20),
    country       varchar(30),
    city          varchar(50),
    state         varchar(50),
    postal_code   varchar(10),
    region        varchar(20),
    product_id    varchar(20),
    category      varchar(30),
    sub_category  varchar(30),
    product_name  varchar(150),
    sales         decimal(10,2),
    quantity      int,
    discount      decimal(4,2),
    profit        decimal(10,2)
);


-- load data from csv
-- update the path based on where you saved the file
load data infile 'C:/data/superstore.csv'
into table orders
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 rows
(row_id, order_id, @order_date, @ship_date, ship_mode,
 customer_id, customer_name, segment, country, city, state,
 postal_code, region, product_id, category, sub_category,
 product_name, sales, quantity, discount, profit)
set order_date = str_to_date(@order_date, '%m/%d/%Y'),
    ship_date  = str_to_date(@ship_date,  '%m/%d/%Y');

-- quick check
select count(*) from orders;


-- 1. overall business summary
select
    count(distinct order_id) as total_orders,
    round(sum(sales), 2) as total_sales,
    round(sum(profit), 2) as total_profit,
    round(sum(profit) / sum(sales) * 100, 2) as margin_pct
from orders;


-- 2. sales and profit by category
select
    category,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit,
    round(sum(profit) / sum(sales) * 100, 2) as margin_pct
from orders
group by category
order by sales desc;


-- 3. region wise performance
select
    region,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit,
    count(distinct order_id) as orders
from orders
group by region
order by sales desc;


-- 4. monthly sales trend - to check seasonality
select
    year(order_date) as yr,
    month(order_date) as mn,
    round(sum(sales), 2) as monthly_sales
from orders
group by year(order_date), month(order_date)
order by yr, mn;


-- 5. top 10 products by revenue
select
    product_name,
    round(sum(sales), 2) as total_sales,
    sum(quantity) as units
from orders
group by product_name
order by total_sales desc
limit 10;


-- 6. sub categories that are losing money
select
    sub_category,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit
from orders
group by sub_category
order by profit asc
limit 5;


-- 7. how discounts are affecting profit
select
    case
        when discount = 0 then 'no discount'
        when discount <= 0.10 then '1-10%'
        when discount <= 0.20 then '11-20%'
        when discount <= 0.30 then '21-30%'
        else 'above 30%'
    end as discount_bucket,
    count(*) as num_orders,
    round(avg(profit), 2) as avg_profit,
    round(sum(profit), 2) as total_profit
from orders
group by discount_bucket
order by avg_profit desc;


-- 8. top customers by revenue
select
    customer_name,
    segment,
    round(sum(sales), 2) as total_sales,
    round(sum(profit), 2) as total_profit,
    count(distinct order_id) as orders
from orders
group by customer_name, customer_id, segment
order by total_sales desc
limit 10;


-- 9. segment breakdown
select
    segment,
    count(distinct customer_id) as customers,
    round(sum(sales), 2) as sales,
    round(avg(sales), 2) as avg_order_value,
    round(sum(profit), 2) as profit
from orders
group by segment
order by sales desc;


-- 10. top 5 states
select
    state,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit,
    count(distinct order_id) as orders
from orders
group by state
order by sales desc
limit 5;


-- 11. shipping mode analysis
select
    ship_mode,
    count(*) as orders,
    round(count(*) * 100.0 / (select count(*) from orders), 1) as pct,
    round(avg(datediff(ship_date, order_date)), 1) as avg_days,
    round(sum(profit), 2) as profit
from orders
group by ship_mode
order by orders desc;


-- 12. year over year sales
select
    year(order_date) as yr,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit
from orders
group by year(order_date)
order by yr;


-- 13. most profitable products (min 1000 in sales)
select
    product_name,
    sub_category,
    round(sum(sales), 2) as sales,
    round(sum(profit), 2) as profit,
    round(sum(profit) / sum(sales) * 100, 2) as margin_pct
from orders
group by product_name, sub_category
having sum(sales) > 1000
order by margin_pct desc
limit 10;


-- 14. orders losing money due to high discounts
select
    order_id,
    customer_name,
    product_name,
    round(sales, 2) as sales,
    discount,
    round(profit, 2) as profit
from orders
where profit < 0
  and discount > 0.20
order by profit asc
limit 10;


-- 15. single query dashboard - all key numbers
select
    round(sum(sales), 2) as total_sales,
    round(sum(profit), 2) as total_profit,
    round(sum(profit) / sum(sales) * 100, 2) as margin_pct,
    count(distinct order_id) as total_orders,
    count(distinct customer_id) as total_customers,
    round(avg(sales), 2) as avg_order_value,
    round(sum(case when profit < 0 then 1 else 0 end) * 100.0 / count(*), 1) as pct_loss_orders,
    round(avg(discount) * 100, 1) as avg_discount_pct
from orders;


-- creating a view for power bi
create or replace view vw_orders as
select
    order_id,
    order_date,
    year(order_date) as order_year,
    month(order_date) as order_month,
    ship_mode,
    customer_name,
    segment,
    region,
    state,
    category,
    sub_category,
    product_name,
    sales,
    quantity,
    discount,
    profit,
    round(profit / sales * 100, 2) as margin_pct,
    case when profit >= 0 then 'profitable' else 'loss' end as order_status
from orders
where sales > 0;

select * from vw_orders limit 5;
