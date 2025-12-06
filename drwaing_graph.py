import matplotlib.pyplot as plt
import pandas as pd
import math


csv_file = "csvs/csv_1764930995.csv"
df = pd.read_csv(csv_file)


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


answer_course = Draw_Correct_Course()
answer_course.add_course(start_pos=(0, 0), end_pos=(351, 0))
answer_course.add_course(end_pos=(351, -506))
x_range, y_range = answer_course.get_course()

answer_direct_course = Draw_Correct_Course()
answer_course.add_course(start_pos=(0, 0), end_pos=(351, -506))

## x축, y축 그리는 부분
x_min = df['x_pos'].min() if df['x_pos'].min() < min(x_range) else min(x_range)
y_min = df['y_pos'].min() if df['y_pos'].min() < min(y_range) else min(y_range)
x_max = df['x_pos'].max() if df['x_pos'].max() > max(x_range) else max(x_range)
y_max = df['y_pos'].max() if df['y_pos'].max() > max(y_range) else max(y_range)
plt.hlines(0, x_min-(abs(abs(x_max)-abs(x_min)))*0.3, x_max+(abs(abs(x_max)-abs(x_min)))*0.3, ls=':', colors='gray') # x축 긋기
plt.vlines(0, y_min-(abs(abs(y_max)-abs(y_min)))*0.3, y_max+(abs(abs(y_max)-abs(y_min)))*0.3, ls=':', colors='gray') # y축 긋기

## 선 그리는 부분(드론의 진행 방향, 수평 수직의 올바른 진행 방향)
plt.plot(df['x_pos'], df['y_pos'], label='actual_route', color='red')
plt.plot(x_range, y_range, ls='--', label='correct_route', color='skyblue')

# 시작점과 목표점
target_x, target_y = 351, -506
start_x, start_y = 0, 0

# 벡터 합 연산(드론이 나아갈 방향 그리는 코드)
x_diff = target_x - start_x
y_diff = target_y - start_y
tan_theta = y_diff / x_diff # tan(theta) 함수 값
theta_radian = math.atan2(y_diff, x_diff) # theta 함수 값(라디안)
theta_degree = (theta_radian*180) / math.pi # thata 함수 값(60분법)
print(f"theta 각(라디안): {theta_radian:.3f})")
print(f"theta 각(60분법): {theta_degree:.3f}")
vector_value = 100 # 벡터 값(벡터의 길이)
vector_x = vector_value * math.cos(theta_radian) # 벡터 x 성분
vector_y = vector_value * math.sin(theta_radian) # 벡터 y 성분
plt.arrow(start_x, start_y, vector_x, vector_y, head_length = 20.0, head_width =20.0, width=10.0, fc='red', ec='black') # 벡터 그리기

# 벡터가 맞는지 확인하기 위한 점선 (화살표랑 점선이 서로 겹치면 벡터 연산이 맞다는 의미)
plt.plot((start_x, target_x), (start_y, target_y), ls="--", color = 'blue', label='correct_direct_route')

## 완성된 그림 띄우는 부분
plt.grid()
plt.legend()
plt.axis('equal') # x축과 y축 간격 일정하게
plt.show()