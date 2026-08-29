import os
import pandas as pd
from sqlalchemy import create_engine

# 1. Caminhos do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
DATABASE_PATH = os.path.join(PROCESSED_DATA_DIR, "olist.db")

def export_views():
    """Lê as views analíticas do SQLite e exporta em CSVs tratados para o Power BI."""
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    
    views_to_export = [
        ("vw_fact_orders", "fact_orders.csv"),
        ("vw_dim_products", "dim_products.csv"),
        ("order_items", "dim_order_items.csv"),
        ("order_payments", "dim_order_payments.csv")
    ]
    
    print("Iniciando exportação das tabelas analíticas para o Power BI...\n")
    
    for view_name, output_file in views_to_export:
        print(f"-> Exportando '{view_name}'...")
        query = f"SELECT * FROM {view_name}"
        df = pd.read_sql(query, con=engine)
        
        output_path = os.path.join(PROCESSED_DATA_DIR, output_file)
        df.to_csv(output_path, index=False, encoding="utf-8")
        
        print(f"   [OK] Salvo em: {output_path} ({len(df):,} linhas)\n")
        
    print("Exportação concluída com sucesso! Os arquivos estão prontos para o Power BI.")

if __name__ == "__main__":
    export_views()