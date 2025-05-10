import os
import glob
import pandas as pd
import ta
from src.config import DATA_DIR

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquecer o DataFrame OHLCV com indicadores técnicos.
    Recebe df com colunas: timestamp, open, high, low, close, volume, date.
    Retorna df com colunas adicionais:
      - sma20, ema50, rsi14, macd, atr14, obv
    """
    # Garante ordem temporal
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Indicadores de tendência
    df['sma20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['macd'] = ta.trend.macd_diff(df['close'])

    # Indicadores de momentum
    df['rsi14'] = ta.momentum.rsi(df['close'], window=14)

    # Volatilidade e volume
    df['atr14'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])

    # Remove linhas iniciais com NaNs
    df = df.dropna().reset_index(drop=True)
    return df

def main():
    """
    Processa todos os arquivos OHLCV em DATA_DIR/ohlcv, gera features
    e salva em DATA_DIR/features como SYMBOL_feat.csv.
    """
    ohlcv_dir = os.path.join(DATA_DIR, 'ohlcv')
    features_dir = os.path.join(DATA_DIR, 'features')
    os.makedirs(features_dir, exist_ok=True)

    for filepath in glob.glob(os.path.join(ohlcv_dir, '*.csv')):
        symbol = os.path.splitext(os.path.basename(filepath))[0]
        try:
            df_ohlcv = pd.read_csv(filepath)
            df_feat = generate_features(df_ohlcv)
            out_path = os.path.join(features_dir, f"{symbol}_feat.csv")
            df_feat.to_csv(out_path, index=False)
            print(f"[OK] Features para {symbol} → {out_path}")
        except Exception as e:
            print(f"[ERRO] {symbol}: {e}")

if __name__ == '__main__':
    main()
