import matplotlib.pyplot as plt
import pandas as pd

# 보정 노
# df = pd.read_csv("csv_files/mycsv_1764145716.csv")
# df = pd.read_csv('csv_files/mycsv_1764144732.csv')
df = pd.read_csv("csvs/csv_1764572974.csv")
df = df.loc[1:]

# # 보정 예스
# df = pd.read_csv("")

# # 이상 경로 구하는 함수(그래프 그리기용, 사각형)
# def draw_correct_route_data(start, end):
#     x_1, y_1 = start
#     x_2, y_2 = end
#     if x_1 > x_2:
#         x_range = [i for i in range(x_1, x_2, -1)] + [x_2]*100 + [i for i in range(x_2, x_1)] + [x_1]*100
#     else:
#         x_range = [i for i in range(x_1, x_2)] + [x_2]*100 + [i for i in range(x_2, x_1, -1)] + [x_1]*100
#     if y_1 > y_2:
#         y_range = [y_1]*100 + [i for i in range(y_1, y_2, -1)] + [y_2]*100 + [i for i in range(y_2, y_1)]
#     else:
#         y_range = [y_1]*100 + [i for i in range(y_1, y_2)] + [y_2]*100 + [i for i in range(y_2, y_1, -1)]
#     return x_range, y_range

class Draw_Correct_Course:
    def __init__(self):
        self.x_course = []
        self.y_course = []
    
    def add_course(self, start_pos, end_pos):
        x_1, y_1 = start_pos
        x_2, y_2 = end_pos
        if x_1 > x_2:
            x_range = [i for i in range(x_1, x_2, -1)] + [x_2]*100 + [i for i in range(x_2, x_1)] + [x_1]*100
        else:
            x_range = [i for i in range(x_1, x_2)] + [x_2]*100 + [i for i in range(x_2, x_1, -1)] + [x_1]*100
        
        if y_1 > y_2:
            y_range = [y_1]*100 + [i for i in range(y_1, y_2, -1)] + [y_2]*100 + [i for i in range(y_2, y_1)]
        else:
            y_range = [y_1]*100 + [i for i in range(y_1, y_2)] + [y_2]*100 + [i for i in range(y_2, y_1, -1)]
        
        self.x_course = self.x_course + x_range
        self.y_course = self.y_course + y_range
    
    def get_course(self):
        return self.x_course, self.y_course


# x_range, y_range = draw_correct_route_data((0, 0), (100, -100))
# x_range, y_range = [i for i in range(0, 101)], [0 for i in range(101)]
answer_course = Draw_Correct_Course()
answer_course.add_course(start_pos=(0, 0), end_pos=(100, 0))
answer_course.add_course(start_pos=(100, 0), end_pos=(100, 100))
answer_course.add_course(start_pos=(100, 100), end_pos=(0, 100))
answer_course.add_course(start_pos=(0, 100), end_pos=(0, 0))
x_range, y_range = answer_course.get_course()

plt.plot(df['x_pos'], df['y_pos'], label='actual_route', color='red')
plt.plot(x_range, y_range, ls='--', label='correct_route', color='blue')
plt.hlines(0, -30, 120, ls=':', colors='gray') # x축 긋기
plt.vlines(0, -150, 25, ls=':', colors='gray') # y축 긋기

plt.grid()
plt.legend()
plt.show()