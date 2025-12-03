import matplotlib.pyplot as plt
import pandas as pd

# 보정 노
# df = pd.read_csv("csv_files/mycsv_1764145716.csv")
# df = pd.read_csv('csv_files/mycsv_1764144732.csv')
# df = pd.read_csv("csvs/csv_1764631837.csv") # 개잘된거 1
# df = pd.read_csv("csvs/csv_1764632162.csv") # 개잘된거 2
# df = pd.read_csv("csvs/csv_1764645122.csv") # 가장 잘 된 거
df = pd.read_csv("csvs/csv_1764645744.csv")


class Draw_Correct_Course:
    '''
    ### 경로를 구하기 위한 클래스
    '''
    def __init__(self):
        self.x_course = []
        self.y_course = []
    
    def add_course(self, start_pos=(None, None), end_pos=(0, 0)):
        """
        ## 경로를 추가하는 함수
        - 객체 최초 생성 후 경로를 처음 그리는 경우엔 start_pos를 반드시 채워넣어야 합니다.
        - 일단 한 번 add_course() 함수를 통해 경로를 추가한 경우, 이 다음부터 호출되는 add_course() 함수에서 start_pos 인자를 채우지 않아야 이전 경로에 이어서 새 경로를 추가합니다.
        """
        x_1, y_1 = start_pos
        x_2, y_2 = end_pos

        if x_1 == None and y_1 == None:
            x_1, y_1 = self.x_course[-1], self.y_course[-1]
            x_range = [x_1, x_2]
            y_range = [y_1, y_2]
            self.x_course = self.x_course + x_range
            self.y_course = self.y_course + y_range
            return

        if x_1 > x_2:
            # x_range = [i for i in range(x_1, x_2, -1)]
            x_range = [x_2, x_1]
        elif x_1 == x_2:
            x_range = [x_1, x_1]
        else:
            # x_range = [i for i in range(x_1, x_2)]
            x_range = [x_1, x_2]
        
        if y_1 > y_2:
            # y_range = [y_1]*100 + [i for i in range(y_1, y_2, -1)] + [y_2]*100 + [i for i in range(y_2, y_1)]
            y_range = [y_2, y_1]
        elif y_1 == y_2:
            y_range = [y_1, y_1]
        else:
            # y_range = [y_1]*100 + [i for i in range(y_1, y_2)] + [y_2]*100 + [i for i in range(y_2, y_1, -1)]
            y_range = [y_1, y_2]
        
        self.x_course = self.x_course + x_range
        self.y_course = self.y_course + y_range
    
    def get_course(self):
        return self.x_course, self.y_course

## 정답 경로 생성하는 부분
answer_course = Draw_Correct_Course()
answer_course.add_course(start_pos=(0, 0), end_pos=(100, 0))
answer_course.add_course(end_pos=(100, 100))
answer_course.add_course(end_pos=(0, 100))
answer_course.add_course(end_pos=(0, 0))
x_range, y_range = answer_course.get_course()

## 선 그리는 부분
plt.plot(df['x_pos'], df['y_pos'], label='actual_route', color='red')
plt.plot(x_range, y_range, ls='--', label='correct_route', color='blue')

## x축, y축 그리는 부분
x_min = df['x_pos'].min() if df['x_pos'].min() < min(x_range) else min(x_range)
y_min = df['y_pos'].min() if df['y_pos'].min() < min(y_range) else min(y_range)
x_max = df['x_pos'].max() if df['x_pos'].max() > max(x_range) else max(x_range)
y_max = df['y_pos'].max() if df['y_pos'].max() > max(y_range) else max(y_range)

plt.hlines(0, x_min-10, x_max+10, ls='dashdot', colors='black') # x축 긋기
plt.vlines(0, y_min-10, y_max+10, ls='dashdot', colors='black') # y축 긋기

## 완성된 그림 띄우는 부분
plt.grid()
plt.legend()
plt.show()