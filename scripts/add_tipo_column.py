import pandas as pd
import os

def add_tipo_column(file_path):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Add the 'tipo' column with the value 'AVIARIO' to all rows
        df['tipo'] = 'AVIARIO'

        # Save the modified DataFrame back to the CSV file
        df.to_csv(file_path, index=False)
        print(f"Coluna 'tipo' adicionada com sucesso e preenchida com 'AVIARIO' em {file_path}")
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} nao foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    # Define the path to the aviarios.csv file
    csv_file_path = "data/raw/aviarios.csv"
    add_tipo_column(csv_file_path)
