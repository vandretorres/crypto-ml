import os
import csv
import time
import ccxt
import pandas as pd
from src.config import EXCHANGE_ID, DATA_DIR

# Lista de moedas de cotação em ordem de preferência
QUOTE_CURRENCIES = ["USDT", "BUSD", "USDC"]

def fetch_ohlcv_for(symbol: str, since: int = None, limit: int = None) -> pd.DataFrame:
    """
    Busca OHLCV diário de `symbol` em um par suportado pela exchange.
    Tenta, na ordem, SYMBOL/USDT, SYMBOL/BUSD e SYMBOL/USDC.
    since: timestamp em ms; limit: número de velas.
    Retorna DataFrame com colunas: timestamp, open, high, low, close, volume, date.
    """
    # Inicializa a exchange
    exchange = getattr(ccxt, EXCHANGE_ID)()
    # Carrega mercados disponíveis
    exchange.load_markets()

    # Identifica par disponível
    market_pair = None
    for quote in QUOTE_CURRENCIES:
        pair = f"{symbol}/{quote}"
        if pair in exchange.markets:
            market_pair = pair
            break
    if market_pair is None:
        raise ValueError(f"Nenhum par suportado para {symbol}")

    print(f"--> Buscando {market_pair} …")
    bars = exchange.fetch_ohlcv(market_pair, timeframe='1d', since=since, limit=limit)

    # Constrói DataFrame
    df = pd.DataFrame(bars, columns=['timestamp','open','high','low','close','volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def main():
    """
    Lê `data/top50.csv`, faz o download de OHLCV para cada símbolo
    e salva em `DATA_DIR/ohlcv/SYMBOL.csv`.
    """
    top50_file = os.path.join(DATA_DIR, 'top50.csv')
    if not os.path.exists(top50_file):
        print(f"[ERRO] Arquivo não encontrado: {top50_file}")
        return

    # Lê símbolos do top50
    symbols = []
    with open(top50_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbols.append(row['symbol'])

    # Prepara diretório de saída
    ohlcv_dir = os.path.join(DATA_DIR, 'ohlcv')
    os.makedirs(ohlcv_dir, exist_ok=True)
    since = None  # Pode definir timestamp em ms para histórico limitado
    limit = None  # Padrão: máximo permitido pela exchange

    # Loop de download
    for sym in symbols:
        try:
            df = fetch_ohlcv_for(sym, since=since, limit=limit)
            out_path = os.path.join(ohlcv_dir, f"{sym}.csv")
            df.to_csv(out_path, index=False)
            print(f"[OK]  {sym} → {out_path}\n")
        except ValueError as ve:
            print(f"[SKIP] {sym}: {ve}")
        except Exception as e:
            print(f"[ERRO] {sym}: {e}")
        # Respeita rate limit da exchange
        time.sleep(1.2)

if __name__ == '__main__':
    main()
