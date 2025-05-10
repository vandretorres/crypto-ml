import os
import glob
import pandas as pd
from src.config import DATA_DIR

# Parâmetros de labeling
HORIZON = 7       # horizonte em dias para calcular retorno futuro
THRESHOLD = 0.05  # limiar de retorno para definir sinal de compra


def generate_labels(df: pd.DataFrame, horizon: int = HORIZON, threshold: float = THRESHOLD) -> pd.DataFrame:
    """
    Gera labels de compra (1) ou não (0) com base no retorno futuro.
    - Cria coluna 'future_return' com pct_change no período Horizon e shift(-horizon).
    - Cria coluna 'label' onde future_return > threshold.
    """
    df = df.sort_values('date').reset_index(drop=True)
    # Calcula retorno futuro
    df['future_return'] = df['close'].pct_change(periods=horizon).shift(-horizon)
    # Gera label binária
    df['label'] = (df['future_return'] > threshold).astype(int)
    # Remove linhas com NaN (início e final)
    return df.dropna().reset_index(drop=True)


def main():
    """
    Lê todos os arquivos de features em DATA_DIR/features,
    gera labels e salva em DATA_DIR/labels/SYMBOL_label.csv.
    """
    features_dir = os.path.join(DATA_DIR, 'features')
    labels_dir = os.path.join(DATA_DIR, 'labels')
    os.makedirs(labels_dir, exist_ok=True)

    for filepath in glob.glob(os.path.join(features_dir, '*_feat.csv')):
        symbol = os.path.basename(filepath).split('_')[0]
        try:
            df_feat = pd.read_csv(filepath, parse_dates=['date'])
            df_lab = generate_labels(df_feat)
            out_path = os.path.join(labels_dir, f"{symbol}_label.csv")
            df_lab.to_csv(out_path, index=False)
            print(f"[OK] Labels para {symbol} → {out_path}")
        except Exception as e:
            print(f"[ERRO] {symbol}: {e}")

if __name__ == '__main__':
    main()
