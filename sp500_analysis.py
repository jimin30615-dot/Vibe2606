import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

INPUT_CSV = Path('S&P 500 과거 데이터 (1).csv')
OUTPUT_PNG = Path('sp500_close_2000_2019.png')

# CSV 불러오기
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change']
df = pd.read_csv(INPUT_CSV, encoding='utf-8-sig', names=cols, header=0, skip_blank_lines=True)

# 문자열 정리
if df['Date'].dtype == object:
    df['Date'] = df['Date'].astype(str).str.replace(' ', '', regex=False)
    df = df[df['Date'].str.match(r'\d{4}-\d{2}-\d{2}')]

# 숫자 컬럼 정리
for col in ['Open', 'High', 'Low', 'Close']:
    df[col] = df[col].astype(str).str.replace(',', '', regex=False).replace({'': None})
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 날짜 타입 변환
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')

# 2000-01-01 ~ 2019-12-31 필터링
mask = (df['Date'] >= '2000-01-01') & (df['Date'] <= '2019-12-31')
df = df.loc[mask].copy()
df = df.sort_values('Date').reset_index(drop=True)

# 요약 통계
summary = {
    'count': int(df['Close'].count()),
    'start_date': str(df['Date'].iloc[0].date()),
    'end_date': str(df['Date'].iloc[-1].date()),
    'start_close': float(df['Close'].iloc[0]),
    'end_close': float(df['Close'].iloc[-1]),
    'min_close': float(df['Close'].min()),
    'max_close': float(df['Close'].max()),
    'mean_close': float(df['Close'].mean()),
    'median_close': float(df['Close'].median()),
    'std_close': float(df['Close'].std()),
    'pct_change_total': float((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100),
}

print('S&P 500 2000-01-01 to 2019-12-31 summary:')
for key, value in summary.items():
    print(f'{key}: {value}')

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Close'], color='blue', linewidth=1)
plt.title('S&P 500 Close Price (2000-01-01 to 2019-12-31)')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150)
print('Saved line plot to', OUTPUT_PNG.resolve())

try:
    plt.show()
except Exception:
    pass

try:
    os.startfile(OUTPUT_PNG)
except Exception:
    pass
