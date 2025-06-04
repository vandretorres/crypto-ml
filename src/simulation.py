import os
import json
import argparse
from datetime import datetime
import pandas as pd
import ccxt
from src.config import DATA_DIR

# Configuração de taxas de rede (USD) por ativo; personalize conforme necessário
DEFAULT_NETWORK_FEE = 2.0  # taxa padrão se ativo não estiver em NETWORK_FEES
NETWORK_FEES = {
    'BTC': 5.0,
    'ETH': 10.0,
    # adicione mais símbolos se desejar
}

# Cotação preferencial
QUOTE_CURRENCIES = ['USDT', 'BUSD', 'USDC']

# Inicializa exchange CCXT Binance
exchange = ccxt.binance({'enableRateLimit': True})
exchange.load_markets()

def fetch_price(symbol: str) -> float:
    """Retorna o último preço de mercado do símbolo usando os pares de cotação definidos."""
    for quote in QUOTE_CURRENCIES:
        pair = f"{symbol}/{quote}"
        if pair in exchange.markets:
            ticker = exchange.fetch_ticker(pair)
            price = ticker.get('last')
            if price is not None:
                return float(price)
    raise ValueError(f"Não foi possível obter preço para {symbol} em {QUOTE_CURRENCIES}")

def fetch_exchange_fee(symbol: str) -> float:
    """Retorna a taxa taker para o melhor par disponível, ou fallback padrão."""
    for quote in QUOTE_CURRENCIES:
        pair = f"{symbol}/{quote}"
        try:
            fees = exchange.fetch_trading_fees()
            fee = fees.get(pair, {}).get('taker')
            if fee is not None:
                return float(fee)
        except Exception:
            continue
    # fallback padrão
    return 0.001

def simulate_purchase(investment: float):
    """
    Lê buy_signals.json, simula compra hoje com investimento total em USD,
    e salva em data/simulations/purchase_YYYY-MM-DD.csv
    """
    signals_path = os.path.join(DATA_DIR, 'buy_signals.json')
    if not os.path.exists(signals_path):
        print("Arquivo buy_signals.json não encontrado.")
        return

    symbols = json.load(open(signals_path))
    if not symbols:
        print("Nenhum sinal de compra para simular.")
        return

    per_asset = investment / len(symbols)
    records = []
    for symbol in symbols:
        try:
            price = fetch_price(symbol)
            quantity = per_asset / price
            fee_rate = fetch_exchange_fee(symbol)
            exchange_fee = fee_rate * per_asset
            network_fee = NETWORK_FEES.get(symbol, DEFAULT_NETWORK_FEE)
            total_cost = per_asset + exchange_fee + network_fee
            records.append({
                'symbol': symbol,
                'price': price,
                'quantity': quantity,
                'asset_cost': per_asset,
                'exchange_fee': exchange_fee,
                'network_fee': network_fee,
                'total_cost': total_cost
            })
        except Exception as e:
            print(f"Erro ao simular {symbol}: {e}")
            continue

    if not records:
        print("Nenhuma simulação realizada.")
        return

    df = pd.DataFrame(records)
    sim_dir = os.path.join(DATA_DIR, 'simulations')
    os.makedirs(sim_dir, exist_ok=True)
    filename = f"purchase_{datetime.now():%Y-%m-%d}.csv"
    out_path = os.path.join(sim_dir, filename)
    df.to_csv(out_path, index=False)
    print(f"Simulação salva em: {out_path}")

def evaluate_simulation(sim_file: str):
    """
    Lê CSV de simulação e calcula lucro/prejuízo atual.
    Salva em *_eval.csv, exibe resultado tabular e um resumo final.
    """
    import locale
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    if not os.path.exists(sim_file):
        print(f"Arquivo de simulação não encontrado: {sim_file}")
        return

    df = pd.read_csv(sim_file)
    if df.empty:
        print("Arquivo de simulação vazio.")
        return

    eval_records = []
    for _, row in df.iterrows():
        symbol = row['symbol']
        try:
            current_price = fetch_price(symbol)
            current_value = current_price * row['quantity']
            profit = current_value - row['total_cost']
            profit_pct = profit / row['total_cost'] if row['total_cost'] else 0.0
            rec = row.to_dict()
            rec.update({
                'current_price': current_price,
                'current_value': current_value,
                'profit': profit,
                'profit_pct': profit_pct
            })
            eval_records.append(rec)
        except Exception as e:
            print(f"Erro ao avaliar {symbol}: {e}")
            continue

    if not eval_records:
        print("Nenhuma avaliação realizada.")
        return

    df_eval = pd.DataFrame(eval_records)
    out_file = sim_file.replace('.csv', '_eval.csv')
    df_eval.to_csv(out_file, index=False)
    print(f"[✅] Avaliação salva em: {out_file}")

    # Formatação para exibição
    df_fmt = df_eval[['symbol', 'quantity', 'price', 'total_cost', 'current_value', 'profit', 'profit_pct']].copy()
    df_fmt['quantity'] = df_fmt['quantity'].apply(lambda x: f"{x:.8f}")
    df_fmt['price'] = df_fmt['price'].apply(lambda x: f"${x:,.4f}")
    df_fmt['total_cost'] = df_fmt['total_cost'].apply(lambda x: locale.currency(x, grouping=True))
    df_fmt['current_value'] = df_fmt['current_value'].apply(lambda x: locale.currency(x, grouping=True))
    df_fmt['profit'] = df_fmt['profit'].apply(lambda x: locale.currency(x, grouping=True))
    df_fmt['profit_pct'] = df_fmt['profit_pct'].apply(lambda x: f"{x:.2%}")

    # Exibe tabela
    print("\n📊 Resultado da Avaliação:\n")
    print(df_fmt.to_string(index=False))

    # Sumário
    total_investido = df_eval['total_cost'].sum()
    total_valor = df_eval['current_value'].sum()
    total_lucro = total_valor - total_investido
    total_pct = (total_lucro / total_investido) if total_investido else 0.0

    print("\n📈 Resumo Final:")
    print(f"➡️  Total Investido: {locale.currency(total_investido, grouping=True)}")
    print(f"💰 Lucro/Prejuízo:  {locale.currency(total_lucro, grouping=True)}")
    print(f"📊 Variação (%):    {total_pct:.2%}")
    

def main():
    parser = argparse.ArgumentParser(description="Simulação e avaliação de sinais de compra")
    parser.add_argument('--simulate', action='store_true', help='Executa simulação de compra hoje')
    parser.add_argument('--evaluate', type=str, help='Avalia arquivo de simulação (CSV)')
    parser.add_argument('--investment', type=float, default=1000.0, help='Valor total a investir em USD')
    args = parser.parse_args()

    if args.simulate:
        simulate_purchase(args.investment)
    elif args.evaluate:
        evaluate_simulation(args.evaluate)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
