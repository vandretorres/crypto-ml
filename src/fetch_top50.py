import os
import csv
from pycoingecko import CoinGeckoAPI
from src.config import VS_CURRENCY, DATA_DIR

def fetch_top50():
    """
    Busca as 50 maiores criptomoedas por market cap no CoinGecko
    e salva em data/top50.csv com colunas: rank, symbol, name, market_cap.
    """
    cg = CoinGeckoAPI()
    top50_data = cg.get_coins_markets(
        vs_currency=VS_CURRENCY,
        order='market_cap_desc',
        per_page=50,
        page=1,
        sparkline=False
    )

    # Garante diretório de dados
    os.makedirs(DATA_DIR, exist_ok=True)
    output_file = os.path.join(DATA_DIR, 'top50.csv')

    # Escreve CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'symbol', 'name', 'market_cap'])
        for coin in top50_data:
            writer.writerow([
                coin.get('market_cap_rank'),
                coin.get('symbol').upper(),
                coin.get('name'),
                coin.get('market_cap')
            ])

    print(f"[OK] Top 50 salvo em: {output_file}")

if __name__ == '__main__':
    fetch_top50()
