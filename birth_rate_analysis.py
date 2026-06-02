import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

INPUT_XLSX = Path('출생아수__합계출산율__자연증가_등_20260602141801.xlsx')
OUTPUT_PNG = Path('birth_rate_line_chart.png')

# ===== 데이터 로드 =====
print('Loading Excel file...')
df_raw = pd.read_excel(INPUT_XLSX, sheet_name='데이터')
print(f'Raw shape: {df_raw.shape}')

# ===== 데이터 클렌징 =====
print('\n=== Data Cleaning ===')

# 첫 번째 행(출생아수) 추출
birth_data = df_raw.iloc[0, 1:].copy()  # 첫 열(행이름) 제외
print(f'Initial birth data count: {len(birth_data)}')

# 연도 추출 (연도 형식 통일)
years = []
values = []
for year_str, value in birth_data.items():
    # 연도 문자열 정리 (예: '2025 p)' -> '2025')
    year_clean = str(year_str).strip().split()[0]
    
    # 연도가 숫자인지 확인
    try:
        year_int = int(year_clean)
        # 1970-2025 범위만 필터링
        if 1970 <= year_int <= 2025:
            years.append(year_int)
            values.append(value)
    except ValueError:
        continue

# 데이터프레임 생성
df = pd.DataFrame({
    'Year': years,
    'Birth_Count': values
})

# 데이터 타입 변환
df['Birth_Count'] = pd.to_numeric(df['Birth_Count'], errors='coerce')

# NaN 제거
df = df.dropna()

# 연도 기준 정렬
df = df.sort_values('Year').reset_index(drop=True)

print(f'After cleaning: {len(df)} records')
print(f'Year range: {df["Year"].min():.0f} - {df["Year"].max():.0f}')
print(f'Missing values: {df.isnull().sum().sum()}')

# ===== 통계 분석 =====
print('\n=== Statistical Analysis ===')
summary = {
    'count': int(df['Birth_Count'].count()),
    'start_year': int(df['Year'].iloc[0]),
    'end_year': int(df['Year'].iloc[-1]),
    'start_birth': float(df['Birth_Count'].iloc[0]),
    'end_birth': float(df['Birth_Count'].iloc[-1]),
    'max_birth': float(df['Birth_Count'].max()),
    'max_birth_year': int(df.loc[df['Birth_Count'].idxmax(), 'Year']),
    'min_birth': float(df['Birth_Count'].min()),
    'min_birth_year': int(df.loc[df['Birth_Count'].idxmin(), 'Year']),
    'mean_birth': float(df['Birth_Count'].mean()),
    'std_birth': float(df['Birth_Count'].std()),
    'pct_change': float((df['Birth_Count'].iloc[-1] / df['Birth_Count'].iloc[0] - 1) * 100),
}

for key, value in summary.items():
    print(f'{key}: {value}')

# ===== 라인 그래프 그리기 =====
print('\nGenerating line chart...')
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df['Year'], df['Birth_Count'], color='steelblue', linewidth=2, marker='o', markersize=3)

# 최대, 최소값에 표시
max_idx = df['Birth_Count'].idxmax()
min_idx = df['Birth_Count'].idxmin()
ax.plot(df.loc[max_idx, 'Year'], df.loc[max_idx, 'Birth_Count'], 
        'go', markersize=8, label=f"Max: {df.loc[max_idx, 'Year']:.0f}")
ax.plot(df.loc[min_idx, 'Year'], df.loc[min_idx, 'Birth_Count'], 
        'ro', markersize=8, label=f"Min: {df.loc[min_idx, 'Year']:.0f}")

ax.set_title('Korea Birth Count (1970-2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Birth Count (명)', fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
fig.autofmt_xdate()

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches='tight')
print(f'Saved chart to {OUTPUT_PNG.resolve()}')

# 샘플 데이터 출력
print('\n=== Sample Data ===')
print('First 5 years:')
print(df.head(5).to_string(index=False))
print('\nLast 5 years:')
print(df.tail(5).to_string(index=False))

# 이미지 표시
try:
    plt.show()
except Exception:
    pass

try:
    os.startfile(OUTPUT_PNG)
except Exception:
    pass
