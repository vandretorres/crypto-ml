# src/config.py
import os
from dotenv import load_dotenv

# 1) procura um arquivo ".env" no diretório atual ou acima
load_dotenv()

# 2) lê as variáveis
EXCHANGE_ID = os.getenv("CCXT_EXCHANGE")      # ex: 'binance'
VS_CURRENCY = os.getenv("CG_CURRENCY")        # ex: 'usd'
DATA_DIR    = os.getenv("DATA_DIR")           # ex: './data'

# 3) checagem simples
if EXCHANGE_ID is None or VS_CURRENCY is None or DATA_DIR is None:
    raise ValueError("Faltam variáveis no .env! Verifique CCXT_EXCHANGE, CG_CURRENCY e DATA_DIR.")
