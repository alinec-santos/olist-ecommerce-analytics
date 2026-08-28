import os
import glob
import pandas as pd
from sqlalchemy import create_engine


# Script que automatiza a carga de todos os arquivos CSV presentes em data/raw diretamente para tabelas relacionais em um banco SQLite. 
# 1. Definir caminhos relativos robustos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
DATABASE_PATH = os.path.join(PROCESSED_DATA_DIR, "olist.db")

def get_engine():
    """Cria e retorna a engine de conexao com o banco SQLite."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    return create_engine(f"sqlite:///{DATABASE_PATH}")

def load_csv_files_to_sqlite():
    """Varre a pasta raw, le os CSVs com Pandas e grava em tabelas no SQLite."""
    engine = get_engine()
    csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))

    if not csv_files:
        print(f"[AVISO] Nenhum arquivo CSV encontrado no diretorio: {RAW_DATA_DIR}")
        return

    print(f"Iniciando ingestao de {len(csv_files)} arquivos para o SQLite...\n")

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        
        # Limpeza do nome do arquivo para padronizar o nome da tabela
        table_name = (
            file_name.replace(".csv", "")
                     .replace("olist_", "")
                     .replace("_dataset", "")
        )

        print(f"-> Ingerindo '{file_name}' como tabela '{table_name}'...")
        
        # Leitura com Pandas
        df = pd.read_csv(file_path)
        
        # Gravacao no banco (if_exists='replace' garante idempotencia)
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        
        print(f"   [OK] Tabela '{table_name}' criada com {len(df):,} linhas.\n")

    print(f"Processo finalizado com sucesso! Banco salvo em: {DATABASE_PATH}")

if __name__ == "__main__":
    load_csv_files_to_sqlite()