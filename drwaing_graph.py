import matplotlib.pyplot as plt
import pandas as pd

# 보정 노
df = pd.read_csv("csv_files/mycsv_1764145716.csv")
# df = pd.read_csv('csv_files/mycsv_1764146840.csv')
df = df.loc[1:]

# # 보정 예스
# df = pd.read_csv("")

# 이상 경로 구하는 함수(그래프 그리기용, 사각형)
def draw_correct_route_data(start, end):
    x_1, y_1 = start
    x_2, y_2 = end
    if x_1 > x_2:
        x_range = [i for i in range(x_1, x_2, -1)] + [x_2]*100 + [i for i in range(x_2, x_1)] + [x_1]*100
    else:
        x_range = [i for i in range(x_1, x_2)] + [x_2]*100 + [i for i in range(x_2, x_1, -1)] + [x_1]*100
    if y_1 > y_2:
        y_range = [y_1]*100 + [i for i in range(y_1, y_2, -1)] + [y_2]*100 + [i for i in range(y_2, y_1)]
    else:
        y_range = [y_1]*100 + [i for i in range(y_1, y_2)] + [y_2]*100 + [i for i in range(y_2, y_1, -1)]
    return x_range, y_range

x_range, y_range = draw_correct_route_data((0, 0), (100, -100))

plt.plot(df['x_pos'], df['y_pos'], label='actual_route', color='red')
plt.plot(x_range, y_range, ls='--', label='correct_route', color='blue')
plt.hlines(0, -30, 120, ls=':', colors='gray') # x축 긋기
plt.vlines(0, -150, 25, ls=':', colors='gray') # y축 긋기

plt.grid()
plt.legend()
plt.show()