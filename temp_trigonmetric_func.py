import math

x_1, y_1 = 1, 1
x_2, y_2 = 2, 1+math.sqrt(3)

x_diff = x_2 - x_1
y_diff = y_2 - y_1

tan_result = y_diff / x_diff

theta = math.atan2(y_diff, x_diff)

print(tan_result) # >>> 1.7320508075688772
print(math.tan(theta)) # >>> 1.7320508075688776
print(math.sqrt(3)) # >>> 1.7320508075688772

total_power = 10
pitch_power = total_power * math.cos(theta)
roll_power = total_power * math.sin(theta)
print(pitch_power) # >>> 5.000000000000001
print(roll_power) # >>> 8.660254037844386
print(pitch_power + roll_power) # >>> 13.660254037844386
print((total_power**2, pitch_power**2 + roll_power**2)) # >>> (100, 100.0)