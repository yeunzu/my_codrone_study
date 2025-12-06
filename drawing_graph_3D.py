import matplotlib.pyplot as plt
import pandas as pd
import math


csv_file = "csvs/csv_1764930995.csv"
df = pd.read_csv(csv_file)

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
ax.plot(df['x_pos'], df['y_pos'], df['z_pos'], label='actual_route', color='red')
ax.plot(x_range, y_range, z_range, ls='--', label='correct_route', color='skyblue')

ax.grid()
ax.legend()
ax.axis('equal')
plt.show()