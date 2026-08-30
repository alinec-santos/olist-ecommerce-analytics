-- ====================================================================
-- 1. View: Fato Pedidos Consolidada (Grão Exato: 1 Linha por Pedido)
-- ====================================================================
DROP VIEW IF EXISTS vw_fact_orders;

CREATE VIEW vw_fact_orders AS
WITH aggregated_items AS (
    SELECT 
        order_id,
        ROUND(SUM(price), 2) AS total_item_value,
        ROUND(SUM(freight_value), 2) AS total_freight_value,
        ROUND(SUM(price + freight_value), 2) AS total_order_value,
        COUNT(order_item_id) AS total_items_count
    FROM order_items
    GROUP BY order_id
)
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    DATE(o.order_purchase_timestamp) AS order_date,
    STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_year_month,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    COALESCE(i.total_item_value, 0) AS total_item_value,
    COALESCE(i.total_freight_value, 0) AS total_freight_value,
    COALESCE(i.total_order_value, 0) AS total_order_value,
    COALESCE(i.total_items_count, 0) AS total_items_count
FROM orders o
INNER JOIN customers c 
    ON o.customer_id = c.customer_id
LEFT JOIN aggregated_items i 
    ON o.order_id = i.order_id;


-- ====================================================================
-- 2. View: Dimensão Produtos Tratada (Com Traduções e Limpeza de Nulos)
-- ====================================================================
DROP VIEW IF EXISTS vw_dim_products;

CREATE VIEW vw_dim_products AS
SELECT 
    p.product_id,
    COALESCE(p.product_category_name, 'nao_informado') AS category_name_pt,
    COALESCE(t.product_category_name_english, 'not_informed') AS category_name_en,
    COALESCE(p.product_weight_g, 0) AS weight_g,
    COALESCE(p.product_length_cm, 0) AS length_cm,
    COALESCE(p.product_height_cm, 0) AS height_cm,
    COALESCE(p.product_width_cm, 0) AS width_cm
FROM products p
LEFT JOIN product_category_name_translation t 
    ON p.product_category_name = t.product_category_name;


-- ====================================================================
-- 3. Queries de Validação e Teste
-- ====================================================================
SELECT 
    order_id, 
    customer_state, 
    order_year_month, 
    total_order_value, 
    total_items_count 
FROM vw_fact_orders 
LIMIT 5;

SELECT * 
FROM vw_dim_products 
LIMIT 5;