import argparse
import sys

# Importa módulos internos
from src.fetch_top50 import fetch_top50
from src.fetch_ohlcv import main as fetch_ohlcv_all
from src.features import main as gen_all_features
from src.label import main as gen_all_labels
from src.model import main as train_all_models
from src.inference import infer_symbol, FEATURE_COLS
from src.config import DATA_DIR
import glob
import os
import pandas as pd


def run_inference():
    from src.inference import infer_symbol
    buy_list = []
    skip_list = []
    features_dir = os.path.join(DATA_DIR, 'features')
    for feat_path in glob.glob(os.path.join(features_dir, '*_feat.csv')):
        symbol = os.path.basename(feat_path).split('_')[0]
        try:
            sig = infer_symbol(symbol)
            if sig == 1:
                buy_list.append(symbol)
        except Exception as e:
            skip_list.append(f"{symbol}: {e}")
    # Exibe
    print("### Sinais de Compra ###")
    print(', '.join(sorted(buy_list)) or "Nenhum sinal de compra no momento.")
    if skip_list:
        print("\n### Erros/Pulos ###")
        print('\n'.join(skip_list))
    # Exporta JSON
    output_json = os.path.join(DATA_DIR, 'buy_signals.json')
    pd.Series(buy_list).to_json(output_json, orient='values')
    print(f"\nSinais exportados em: {output_json}")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline completo de análise de criptomoedas ML"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='Executa todas as etapas na ordem correta')
    group.add_argument('--fetch-top50', action='store_true', help='Busca top50 no CoinGecko')
    group.add_argument('--fetch-ohlcv', action='store_true', help='Baixa dados OHLCV para top50')
    group.add_argument('--features', action='store_true', help='Gera indicadores técnicos (features)')
    group.add_argument('--labels', action='store_true', help='Gera labels de buy/sell')
    group.add_argument('--train', action='store_true', help='Treina modelos para todas as criptos')
    group.add_argument('--infer', action='store_true', help='Executa inferência e gera sinais')

    args = parser.parse_args()

    if args.all:
        fetch_top50()
        fetch_ohlcv_all()
        gen_all_features()
        gen_all_labels()
        train_all_models()
        run_inference()
    elif args.fetch_top50:
        fetch_top50()
    elif args.fetch_ohlcv:
        fetch_ohlcv_all()
    elif args.features:
        gen_all_features()
    elif args.labels:
        gen_all_labels()
    elif args.train:
        train_all_models()
    elif args.infer:
        run_inference()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
