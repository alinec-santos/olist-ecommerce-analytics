-- 1. Contagem volumétrica de registros por tabela
-- Importância: Confere se a carga do Python bateu 100% com os CSVs originais.
SELECT 'orders' AS table_name, COUNT(*) AS total_rows FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers;

-- 2. Entendendo a granularidade e status dos pedidos
-- Importância: No mundo real, você NÃO pode somar faturamento de pedidos cancelados ou indisponíveis.
SELECT 
    order_status,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 3. Verificação do período histórico coberto
-- Importância: Saber o intervalo temporal evita conclusões enviesadas por meses incompletos.
SELECT 
    MIN(order_purchase_timestamp) AS first_order_date,
    MAX(order_purchase_timestamp) AS last_order_date
FROM orders;

-- 4. Análise de unicidade de clientes (customer_id vs customer_unique_id)
-- Pegadinha do dataset Olist:
-- 'customer_id' é uma chave temporária para aquela compra específica.
-- 'customer_unique_id' é o CPF/identificador real da pessoa física.
SELECT 
    COUNT(customer_id) AS total_orders_clients,
    COUNT(DISTINCT customer_unique_id) AS unique_real_customers
FROM customers;