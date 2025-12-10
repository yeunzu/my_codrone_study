import math
import matplotlib.pyplot as plt

def math_test():
    x_1, y_1 = 1, 1
    x_2, y_2 = 2, 1+math.sqrt(3)

    x_diff = x_2 - x_1
    y_diff = y_2 - y_1

    tan_result = y_diff / x_diff

    theta_radian = math.atan2(y_diff, x_diff)
    theta_degree = (180 * theta_radian) / math.pi

    print(f"y_diff / x_diff (tan_result) : {tan_result:.3f}") # >>> 1.7320508075688772
    print(f"math.tan(theta_radian) : {math.tan(theta_radian):.3f}") # >>> 1.7320508075688776
    print(f"math.sqrt(3) : {math.sqrt(3):.3f}") # >>> 1.7320508075688772

    print(f"theta_radian: {theta_radian:.3f}")
    print(f"theta_degree: {theta_degree:.3f}")

    total_power = 10
    pitch_power = total_power * math.cos(theta_radian)
    roll_power = total_power * math.sin(theta_radian)
    print(pitch_power) # >>> 5.000000000000001
    print(roll_power) # >>> 8.660254037844386
    print(pitch_power + roll_power) # >>> 13.660254037844386
    print((total_power**2, pitch_power**2 + roll_power**2)) # >>> (100, 100.0)

def drawing_test_route():
    x_1, y_1 = 0, 0
    x_2, y_2 = 100, 100*math.sqrt(3)

    triangle_x = [x_1, x_2, x_2, x_1]
    triangle_y = [y_1, y_1, y_2, y_1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(triangle_x, triangle_y, color='skyblue', ls='--', label='correct_route')

    vector_value = 50
    x_diff = x_2 - x_1
    y_diff = y_2 - y_1
    tan_theta = y_diff / x_diff
    theta_radian = math.atan2(y_diff, x_diff)
    theta_degree = (180 * theta_radian) / math.pi # 60도
    print(f"라디안 각도: {theta_radian:.3}")
    print(f"60분법 각도: {theta_degree:.3}")
    sin_theta = math.sin(theta_radian)
    cos_theta = math.cos(theta_radian)
    print(f"사인값: {sin_theta:.3f}") # sin(60) = sqrt(3)/2
    print(f"sqrt(3) / 2 = {math.sqrt(3) / 2:.3f}")
    print(f"코사인값: {cos_theta:.3f}") # cos(60) = 1/2
    vector_x = vector_value * cos_theta
    vector_y = vector_value * sin_theta
    # x성분
    ax.arrow(x_1, y_1, vector_x, y_1, head_width=8, width=5, label='calculated_vector_x', color='orange')
    # y성분
    ax.arrow(x_1, y_1, x_1, vector_y, head_width=8, width=5, label='calculated_vector_y', color='green')
    # 벡터 합(x성분 + y성분)
    ax.arrow(x_1, y_1, vector_x, vector_y, head_width=8, width=5, label='calculated_vector', color='purple')

    # 점 표시
    ax.scatter(x_1, y_1, s=40, color='black')
    ax.scatter(x_2, y_2, s=40, color='black')

    ax.text(x_1-55, y_1-8, "now_position\n : (0, 0)")
    ax.text(x_2+10, y_2-10, "target_position\n : (100, 100√3)")

    ax.grid()
    ax.legend()
    ax.axis('equal')
    plt.show()

math_test()
drawing_test_route()