import matplotlib.pyplot as plt
import pandas as pd

# 보정 노
# df = pd.read_csv("csv_files/mycsv_1764145716.csv")
# df = df.loc[1:]

# 보정 예스
df = pd.read_csv("")

plt.plot(df['x_pos'], label='x_pos', ls='-')
plt.plot(df['y_pos'], label='y_pos', ls='--')
plt.plot(df['z_pos'], label='z_pos', ls=':')

plt.grid()
plt.legend()
plt.show()