import matplotlib.pyplot as plt
import pandas as pd
import math


csv_file = "csvs/csv_1765351154.csv" # 1차
df = pd.read_csv(csv_file)

# # 과거 경로 중첩 비교를 위한 데이터 로드(최신 파일을 가장 먼저 불러움)
df_2 = pd.read_csv("csvs/csv_1765351338.csv") # 2차
# df_3 = pd.read_csv("csvs/csv_1764930924.csv")
# df_4 = pd.read_csv("csvs/csv_1764930620.csv")
# df_5 = pd.read_csv("csvs/csv_1764930430.csv")

class Draw_Correct_Course:
    def __init__(self):
        self.x_course = []
        self.y_course = []
        self.z_course = []

    def add_course(self, start_pos=(None, None, None), end_pos=(0, 0, 0)):
        x_1, y_1, z_1 = start_pos
        x_2, y_2, z_2 = end_pos

        if (x_1 == None) and (y_1 == None) and (z_1 == None):
            x_1, y_1, z_1 = self.x_course[-1], self.y_course[-1], self.z_course[-1]
            x_range = [x_1, x_2]
            y_range = [y_1, y_2]
            z_range = [z_1, z_2]
            self.x_course = self.x_course + x_range
            self.y_course = self.y_course + y_range
            self.z_course = self.z_course + z_range
            return
        
        if x_1 > x_2:
            x_range = [x_2, x_1]
        elif x_1 == x_2:
            x_range = [x_1, x_1]
        else:
            x_range = [x_1, x_2]

        if y_1 > y_2:
            y_range = [y_2, y_1]
        elif y_1 == y_2:
            y_range = [y_1, y_1]
        else:
            y_range = [y_1, y_2]

        if z_1 > z_2:
            z_range = [z_2, z_1]
        elif z_1 == z_2:
            z_range = [z_1, z_1]
        else:
            z_range = [z_1, z_2]

        self.x_course = self.x_course + x_range
        self.y_course = self.y_course + y_range
        self.z_course = self.z_course + z_range

    def get_course(self):
        return self.x_course, self.y_course, self.z_course

start_x, start_y = 0, 0
target_x, target_y = 351, -506
answer_course = Draw_Correct_Course()
answer_course.add_course(start_pos=(0, 0, 0), end_pos=(0, 0, 150))
answer_course.add_course(end_pos=(target_x, target_y, 150))
answer_course.add_course(end_pos=(target_x, target_y, 0))
x_range, y_range, z_range = answer_course.get_course()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# 실제로 날아간 경로
ax.plot(df['x_pos'], df['y_pos'], df['z_pos'], label='actual_route', color='red')

# 과거 경로 중첩(최신 데이터를 먼저 그림)
ax.plot(df_2['x_pos'], df_2['y_pos'], df_2['z_pos'], label='actual_route_2', color='orange') # 2치
# ax.plot(df_3['x_pos'], df_3['y_pos'], df_3['z_pos'], label='actual_route_2', color='green')
# ax.plot(df_4['x_pos'], df_4['y_pos'], df_4['z_pos'], label='actual_route_3', color='darkgreen')
# ax.plot(df_5['x_pos'], df_5['y_pos'], df_5['z_pos'], label='actual_route_4', color='darkblue')

# 이상적인 경로
ax.plot(x_range, y_range, z_range, ls='--', label='correct_route', color='skyblue')

ax.grid()
ax.legend()
ax.axis('equal')
plt.show()