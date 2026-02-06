
import yfinance as yf


def check_intervals():
    tickers = ["^BSESN", "TRIDENT.NS"]
    print(f"Checking tickers: {tickers}")
    
    print("\n--- 1 Day Interval (Current Impl) ---")
    data_1d = yf.download(tickers, period="1d", progress=False)
    if not data_1d.empty:
        for t in tickers:
            try:
                price = data_1d['Close'][t].iloc[-1]
                print(f"{t}: {price}")
            except:
                pass

    print("\n--- 1 Minute Interval ---")
    try:
        data_1m = yf.download(tickers, period="1d", interval="1m", progress=False)
        if not data_1m.empty:
             for t in tickers:
                try:
                    price = data_1m['Close'][t].iloc[-1]
                    print(f"{t}: {price}")
                    print(f"Time: {data_1m.index[-1]}")
                except:
                    pass
    except Exception as e:
        print(f"1m fetch failed: {e}")

if __name__ == "__main__":
    check_intervals()
