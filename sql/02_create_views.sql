-- View: Fato Pedidos Consolidada
-- Consolida o grão no nível do pedido com faturamento, frete e status
CREATE VIEW IF NOT EXISTS vw_fact_orders AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    -- Conversoes de data no SQLite
    DATE(o.order_purchase_timestamp) AS order_date,
    STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_year_month,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    -- Metricas financeiras agregadas
    ROUND(COALESCE(SUM(i.price), 0), 2) AS total_item_value,
    ROUND(COALESCE(SUM(i.freight_value), 0), 2) AS total_freight_value,
    ROUND(COALESCE(SUM(i.price + i.freight_value), 0), 2) AS total_order_value,
    COUNT(i.order_item_id) AS total_items_count
FROM orders o
INNER JOIN customers c 
    ON o.customer_id = c.customer_id
LEFT JOIN order_items i 
    ON o.order_id = i.order_id
GROUP BY 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date;
    
SELECT 
    order_id, 
    customer_state, 
    order_year_month, 
    total_order_value, 
    total_items_count 
FROM vw_fact_orders 
LIMIT 5;