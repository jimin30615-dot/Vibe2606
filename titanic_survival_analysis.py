import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

# Titanic dataset from a public GitHub raw source
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

df = pd.read_csv(url)

# 간단한 데이터 확인
print("데이터셋 로드 완료")
print(df.head())
print(f"총 행 수: {len(df)}")

# 성별 생존 비율 계산
survival_ratio = df.groupby("Sex")["Survived"].mean() * 100
survival_ratio = survival_ratio.round(2)
print("\n성별 생존 비율(%)")
print(survival_ratio)

# 막대 그래프 그리기
plt.figure(figsize=(8, 6))
ax = sns.barplot(x=survival_ratio.index, y=survival_ratio.values, palette=["#4c72b0", "#dd8452"])
ax.set_title("Titanic Survival Rate by Sex", fontsize=16)
ax.set_xlabel("Sex", fontsize=12)
ax.set_ylabel("Survival Rate (%)", fontsize=12)
ax.set_ylim(0, 100)

for i, value in enumerate(survival_ratio.values):
    ax.text(i, value + 2, f"{value:.1f}%", ha="center", fontsize=12)

plt.tight_layout()
plt.savefig("titanic_survival_by_sex.png", dpi=150)
plt.show()
