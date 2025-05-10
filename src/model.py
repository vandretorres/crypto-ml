import os
import glob
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, accuracy_score
from src.config import DATA_DIR

def train_and_evaluate(symbol: str, df: pd.DataFrame):
    """
    Treina um RandomForestClassifier usando TimeSeriesSplit e salva o modelo.
    Imprime relatório de classificação do último fold.
    """
    # Define features e label
    feature_cols = ['open', 'high', 'low', 'close', 'volume',
                    'sma20', 'ema50', 'rsi14', 'macd', 'atr14', 'obv']
    X = df[feature_cols]
    y = df['label']

    # TimeSeriesSplit para validação
    tscv = TimeSeriesSplit(n_splits=5)
    model = None
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"--- {symbol} Fold {fold} ---")
        print(classification_report(y_test, y_pred))

    # Treina em todo o conjunto
    final_model = RandomForestClassifier(n_estimators=100, random_state=42)
    final_model.fit(X, y)
    # Salva o modelo
    models_dir = os.path.join(DATA_DIR, 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f"{symbol}_model.joblib")
    joblib.dump(final_model, model_path)
    print(f"[OK] Modelo final para {symbol} salvo em: {model_path}\n")


def main():
    labels_dir = os.path.join(DATA_DIR, 'labels')
    features_dir = os.path.join(DATA_DIR, 'features')

    for label_file in glob.glob(os.path.join(labels_dir, '*_label.csv')):
        symbol = os.path.basename(label_file).split('_')[0]
        feat_file = os.path.join(features_dir, f"{symbol}_feat.csv")
        if not os.path.exists(feat_file):
            print(f"[SKIP] {symbol}: arquivo de features não encontrado.")
            continue

        # Carrega dados
        df_feat = pd.read_csv(feat_file, parse_dates=['date'])
        df_lab = pd.read_csv(label_file, parse_dates=['date'])
        # Faz merge por data para alinhar features e labels
        df = pd.merge(df_feat, df_lab[['date', 'label']], on='date', how='inner')
        df = df.dropna().reset_index(drop=True)

        print(f"\nTreinando modelo para {symbol} com {len(df)} amostras...")
        try:
            train_and_evaluate(symbol, df)
        except Exception as e:
            print(f"[ERRO] {symbol}: {e}\n")

if __name__ == '__main__':
    main()
