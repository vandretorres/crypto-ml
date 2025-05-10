import os
import glob
import pandas as pd
import joblib
from src.config import DATA_DIR

# Diretórios de entrada e saída\FEATURES_DIR = os.path.join(DATA_DIR, 'features')
# Diretórios de saída de modelos
FEATURES_DIR = os.path.join(DATA_DIR, 'features')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# Colunas usadas como features pelo modelo
FEATURE_COLS = [
    'open', 'high', 'low', 'close', 'volume',
    'sma20', 'ema50', 'rsi14', 'macd', 'atr14', 'obv'
]

def infer_symbol(symbol: str) -> int:
    """
    Retorna o sinal de compra (1) ou não (0) para o símbolo.
    Lança ValueError se não houver dados suficientes.
    """
    feat_file = os.path.join(FEATURES_DIR, f"{symbol}_feat.csv")
    if not os.path.exists(feat_file):
        raise FileNotFoundError(f"Features não encontradas para {symbol}")

    df_feat = pd.read_csv(feat_file, parse_dates=['date'])
    if df_feat.empty:
        raise ValueError(f"Sem dados de features suficientes para {symbol}")

    # Seleciona a última linha de features
    last_row = df_feat.iloc[[-1]][FEATURE_COLS]

    model_file = os.path.join(MODELS_DIR, f"{symbol}_model.joblib")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Modelo não encontrado para {symbol}")

    model = joblib.load(model_file)
    signal = model.predict(last_row)[0]
    return int(signal)

if __name__ == '__main__':
    buy_list = []
    skip_list = []

    # Itera sobre todos os arquivos de features gerados
    for feat_path in glob.glob(os.path.join(FEATURES_DIR, '*_feat.csv')):
        symbol = os.path.basename(feat_path).split('_')[0]
        try:
            sig = infer_symbol(symbol)
            if sig == 1:
                buy_list.append(symbol)
        except Exception as e:
            skip_list.append(f"{symbol}: {e}")

    # Exibe sinais de compra
    print("### Sinais de Compra ###")
    if buy_list:
        print(', '.join(sorted(buy_list)))
    else:
        print("Nenhum sinal de compra no momento.")

    # Exibe erros e pulos
    if skip_list:
        print("\n### Erros/Pulos ###")
        for err in skip_list:
            print(err)

    # (Opcional) Exportar sinais de compra para arquivo
    output_json = os.path.join(DATA_DIR, 'buy_signals.json')
    pd.Series(buy_list).to_json(output_json, orient='values')
    print(f"\nSinais exportados em: {output_json}")
import os
import glob
import pandas as pd
import joblib
from src.config import DATA_DIR

# Diretórios de entrada e saída\FEATURES_DIR = os.path.join(DATA_DIR, 'features')
# Diretórios de saída de modelos
FEATURES_DIR = os.path.join(DATA_DIR, 'features')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# Colunas usadas como features pelo modelo
FEATURE_COLS = [
    'open', 'high', 'low', 'close', 'volume',
    'sma20', 'ema50', 'rsi14', 'macd', 'atr14', 'obv'
]

def infer_symbol(symbol: str) -> int:
    """
    Retorna o sinal de compra (1) ou não (0) para o símbolo.
    Lança ValueError se não houver dados suficientes.
    """
    feat_file = os.path.join(FEATURES_DIR, f"{symbol}_feat.csv")
    if not os.path.exists(feat_file):
        raise FileNotFoundError(f"Features não encontradas para {symbol}")

    df_feat = pd.read_csv(feat_file, parse_dates=['date'])
    if df_feat.empty:
        raise ValueError(f"Sem dados de features suficientes para {symbol}")

    # Seleciona a última linha de features
    last_row = df_feat.iloc[[-1]][FEATURE_COLS]

    model_file = os.path.join(MODELS_DIR, f"{symbol}_model.joblib")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Modelo não encontrado para {symbol}")

    model = joblib.load(model_file)
    signal = model.predict(last_row)[0]
    return int(signal)

if __name__ == '__main__':
    buy_list = []
    skip_list = []

    # Itera sobre todos os arquivos de features gerados
    for feat_path in glob.glob(os.path.join(FEATURES_DIR, '*_feat.csv')):
        symbol = os.path.basename(feat_path).split('_')[0]
        try:
            sig = infer_symbol(symbol)
            if sig == 1:
                buy_list.append(symbol)
        except Exception as e:
            skip_list.append(f"{symbol}: {e}")

    # Exibe sinais de compra
    print("### Sinais de Compra ###")
    if buy_list:
        print(', '.join(sorted(buy_list)))
    else:
        print("Nenhum sinal de compra no momento.")

    # Exibe erros e pulos
    if skip_list:
        print("\n### Erros/Pulos ###")
        for err in skip_list:
            print(err)

    # (Opcional) Exportar sinais de compra para arquivo
    output_json = os.path.join(DATA_DIR, 'buy_signals.json')
    pd.Series(buy_list).to_json(output_json, orient='values')
    print(f"\nSinais exportados em: {output_json}")
