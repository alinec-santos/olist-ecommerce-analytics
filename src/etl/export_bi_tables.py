import sqlite3
import pandas as pd
from pathlib import Path

# Raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]

# Caminho exato do banco com os dados
DB_PATH = BASE_DIR / "data" / "processed" / "olist.db"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

print(f"-> Conectando ao banco de dados: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)

# 1. Fact Orders (Grão: exatamente 1 linha por pedido com valores consolidados)
query_fact_orders = """
WITH items_agg AS (
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
INNER JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN items_agg i ON o.order_id = i.order_id
WHERE o.order_id IS NOT NULL AND o.order_id != '';
"""

# 2. Dim Products (Produtos com categoria tratada)
query_dim_products = """
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
    ON p.product_category_name = t.product_category_name
WHERE p.product_id IS NOT NULL AND p.product_id != '';
"""

# 3. Dim Order Items (Itens com preços)
query_dim_order_items = """
SELECT 
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM order_items
WHERE order_id IS NOT NULL AND product_id IS NOT NULL;
"""

# 4. Dim Payments (Formas de Pagamento)
query_dim_payments = """
SELECT 
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM order_payments
WHERE order_id IS NOT NULL;
"""

tables = {
    "fact_orders.csv": query_fact_orders,
    "dim_products.csv": query_dim_products,
    "dim_order_items.csv": query_dim_order_items,
    "dim_order_payments.csv": query_dim_payments
}

for filename, sql in tables.items():
    df = pd.read_sql_query(sql, conn)
    output_file = OUTPUT_DIR / filename
    # Exporta com ponto e vírgula como delimitador e vírgula como separador decimal (Padrão BR)
    df.to_csv(output_file, sep=';', decimal=',', index=False, encoding='utf-8-sig')
    print(f"[OK] Exportado: {filename} -> {len(df):,} linhas")

conn.close()
print("\n-> CSVs exportados com formato decimal brasileiro!")