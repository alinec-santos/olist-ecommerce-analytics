import sqlite3
import pandas as pd
from pathlib import Path

# Configuração de caminhos do projeto
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "processed" / "olist.db"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_segmented_customers.csv"

print(f"-> Conectando ao banco: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)

# 1. Extração dos pedidos consolidados por cliente único
query = """
SELECT 
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp,
    i.price + i.freight_value AS total_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items i ON o.order_id = i.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp IS NOT NULL
"""

df_raw = pd.read_sql_query(query, conn)
conn.close()

df_raw["order_purchase_timestamp"] = pd.to_datetime(df_raw["order_purchase_timestamp"])
print(f"-> Registros carregados: {len(df_raw):,} linhas")

# 2. Cálculo das métricas RFM
# Snapshot definido como 1 dia após a data mais recente da base
snapshot_date = df_raw["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

df_rfm = df_raw.groupby("customer_unique_id").agg({
    "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
    "order_id": "nunique",
    "total_value": "sum"
}).reset_index()

df_rfm.columns = ["customer_unique_id", "recency_days", "frequency", "monetary_value"]

# 3. Atribuição de Scores (1 a 5)
df_rfm["r_score"] = pd.qcut(df_rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
df_rfm["m_score"] = pd.qcut(df_rfm["monetary_value"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Frequência tratada considerando o comportamento da base
df_rfm["f_score"] = df_rfm["frequency"].apply(lambda x: 5 if x >= 3 else (3 if x == 2 else 1))

# 4. Regra de Classificação de Negócio
def define_segment(row):
    r, f, m = row["r_score"], row["f_score"], row["m_score"]
    
    if r >= 4 and f >= 3:
        return "Champions"
    elif r >= 3 and f >= 1 and m >= 4:
        return "Leais com Alto Valor"
    elif r >= 4 and f == 1:
        return "Clientes Recentes"
    elif r == 3:
        return "Potenciais Clientes"
    elif r == 2:
        return "Em Risco de Churn"
    elif r == 1 and m >= 4:
        return "Grandes Contas Inativas"
    else:
        return "Hibernando/Perdidos"

df_rfm["segment"] = df_rfm.apply(define_segment, axis=1)

# 5. Exportação
df_rfm.to_csv(OUTPUT_PATH, sep=";", decimal=",", index=False, encoding="utf-8-sig")

print("\n" + "="*45)
print(" DISTRIBUIÇÃO DOS SEGMENTOS RFM")
print("="*45)
summary = df_rfm["segment"].value_counts()
for seg, count in summary.items():
    pct = (count / len(df_rfm)) * 100
    print(f"{seg:<25}: {count:>6,} ({pct:.1f}%)")

print("="*45)
print(f"-> Arquivo exportado: {OUTPUT_PATH}")