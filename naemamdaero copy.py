from codrone_edu.drone import *
import pandas as pd
import time
import math
from collections.abc import Iterable

# 초기 설정
drone = Drone()
drone.pair()

df = pd.DataFrame(columns=['x_pos', 'y_pos', 'z_pos'])
is_Ctrl_C = False

TIME_DELAY = 0.1

def note_position(df: pd.DataFrame, value: Iterable):
    '''
    DataFrame의 맨 마지막 부분에 입력된 값(value)를 추가하는 것. value는 print()로 출력된다.
    '''
    if len(df.columns) != len(value):
        raise ValueError(f"DataFrame의 열 개수{len(df.columns)}와 value의 원소 개수{len(value)}가 맞지 않습니다.")
    print(value)
    df.loc[len(df)] = value


def go_straight(length: float | int, speed: int = 20):
    '''
    ### 앞으로 가는 함수
    - length: 앞으로 갈 거리를 cm 단위로 받음
    - speed : 드론의 속도를 조정한다. 0 < speed <= 100의 정수만 받는다.
    '''
    if not 0 < speed <= 100:
        raise ValueError('go_to_pos() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.')
    
    global drone, df
    print(f"앞으로{length}cm 이동")
    if length >= 0:
        drone.set_pitch(speed)
    else:
        drone.set_pitch(-speed)
    
    while drone.get_pos_x() <= length:
        pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
        note_position(df=df, value=pos)
        drone.move()
        time.sleep(TIME_DELAY)
    
    drone.set_pitch(0)
    drone.move()
    print("앞으로 이동 종료")


def go_to_pos(target_pos: Iterable = (0, 0), allow_RMSE: float | int = 5, speed: int = 20):
    '''
    ### 드론을 원하는 좌표까지 옮겨주는 함수
    드론 동체의 회전 없이 드론을 원하는 좌표로 이동시킨다.
    - target_pos : 오로지 두 개의 원소만을 가지는 iterable을 받는다. 앞에서부터 순서대로 x, y를 의미한다.
    - allow_RMSE : 허용할 오차 거리이다. 기본값으로는 5(cm)가 적용된다.
    - speed : 드론의 속도를 조정한다. 0 < speed <= 100의 정수만 받는다.
    - TODO: 절댓값으로 처리해서 범위 안에 들어가게 하기
    '''
    if len(target_pos) != 2:
        raise ValueError('go_to_pos() 함수에서 target_pos는 오로지 2개의 원소를 가지는 iterable이어야 합니다.')
    if not 0 < speed <= 100:
        raise ValueError('go_to_pos() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.')
    
    global drone, df

    target_x, target_y = target_pos
    now_x_pos, now_y_pos = drone.get_pos_x(), drone.get_pos_y()

    x_RMSE, y_RMSE = abs(now_x_pos - target_x), abs(now_y_pos - target_y)

    # X 먼저 이동
    print("x 이동 중")
    while x_RMSE > allow_RMSE:
        pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
        note_position(df=df, value=pos)

        drone.set_roll(0)
        if drone.get_pos_x() - target_x < 0: # x가 덜 나간 경우
            drone.set_pitch(speed)
        else: # x가 더 나간 경우
            drone.set_pitch(-speed)
        drone.move()
        time.sleep(TIME_DELAY)
        x_RMSE = abs(drone.get_pos_x() - target_x) # x 오차 업데이트
        print(f'현재 x 오차 : {x_RMSE}')

    # Y 이동
    print("y 이동 중")
    while y_RMSE > allow_RMSE:
        pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
        note_position(df=df, value=pos)

        drone.set_pitch(0)
        if drone.get_pos_y() - target_y < 0: # y가 덜 나간 경우
            drone.set_roll(speed)
        else:
            drone.set_roll(-speed)
        drone.move()
        time.sleep(TIME_DELAY)
        y_RMSE = abs(drone.get_pos_y() - target_y) # y 오차 업데이트
        print(f'현재 y 오차 : {y_RMSE}')

    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()
    print("지정한 좌표까지 이동완료")
    pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
    note_position(df=df, value=pos)
        

def go_to_pos_NoSupport(target_pos: Iterable = (0, 0), speed: int = 20):
    '''
    ### 드론을 원하는 좌표까지 옮겨주는 함수
    드론 동체의 회전 없이 드론을 원하는 좌표로 이동시킨다.
    좌표에 도달하면 동작을 멈추는 단순한 동작만을 한다. 별도의 오차범위를 고려하지 않는다.
    - target_pos : 오로지 두 개의 원소만을 가지는 iterable을 받는다. 앞에서부터 순서대로 x, y를 의미한다.
    - speed : 드론의 속도를 조정한다. 0 < speed <= 100의 정수만 받는다.
    '''
    global drone, df
    target_x, target_y = target_pos
    now_x, now_y = drone.get_pos_x(), drone.get_pos_y()
    if now_x < target_x:
        while now_x < target_x:
            drone.set_pitch(speed)
            drone.move()
            time.sleep(TIME_DELAY)
            now_x, now_y, now_z = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
            note_position(df=df, value=(now_x, now_y, now_z))
    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()

    if now_x > target_x:
        while now_x > target_x:
            drone.set_pitch(-speed)
            drone.move()
            time.sleep(TIME_DELAY)
            now_x, now_y, now_z = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
            note_position(df=df, value=(now_x, now_y, now_z))
    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()

    if now_y < target_y:
        while now_y < target_y:
            drone.set_roll(-speed)
            drone.move()
            time.sleep(TIME_DELAY)
            now_x, now_y, now_z = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
            note_position(df=df, value=(now_x, now_y, now_z))
    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()

    if now_y > target_y:
        while now_y > target_y:
            drone.set_roll(speed)
            drone.move()
            time.sleep(TIME_DELAY)
            now_x, now_y, now_z = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
            note_position(df=df, value=(now_x, now_y, now_z))
    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()


def turn_body(target_angle: float | int):
    '''
    ### 드론의 몸체를 회전하는 함수
    - TODO: 미완성 상태
    '''
    global drone, df
    now_angle = 0 # TODO: 현재 몸체 각도 가져오기
    while abs(now_angle - target_angle) > 0.5: # 각도가 오차범위(0.5) 넘어가면 몸체회전
        drone.set_yaw(20)
        drone.move()
        time.sleep(TIME_DELAY)

    drone.set_yaw(0)
    drone.move()


def landing_assist(stop_z_pos: float | int = 12, target_pos: Iterable = (0,0), allow_RMSE: float | int = 3, support_power: int = 8):
    '''
    ### 착륙 보조하는 함수
    - z축 12cm(기본값, start_z_pos 값으로 수정가능) 위까지 빠르게 낙하
    - 이후 x, y축 보정 후 착륙
        - 목표하는 x, y 좌표(target_pos)를 분석해 허용오차(allow_RMSE)를 초과하면 천천히 보정
        - target_pos는 순서대로 x, y좌표를 의미
    '''
    if len(target_pos) != 2:
        raise ValueError('landing_assist() 함수에서 target_pos는 오로지 2개의 원소를 가지는 iterable이어야 합니다.')
    
    global drone, df

    target_x_pos, target_y_pos = target_pos
    print("착륙 시작")
    while drone.get_pos_z() > stop_z_pos:
        pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
        note_position(df=df, value=pos)
        drone.set_throttle(-30)
        drone.move()
        time.sleep(TIME_DELAY)

    # 목표 높이 이내로 들어오면 높이 조절 정지
    drone.set_throttle(0)
    drone.move()

    print("보정 시작")
    # x, y좌표를 파악해 목표와의 거리 계산
    now_x_pos, now_y_pos = drone.get_pos_x(), drone.get_pos_y()
    RMSE =  math.sqrt((now_x_pos - target_x_pos)**2 + (now_y_pos - target_y_pos)**2)
    print(f"현재 오차 : {RMSE:.3f}")

    while RMSE > allow_RMSE: # 거리가 허용치를 넘어선다면 아래 조정을 반복
        print(f"현재 오차 : {RMSE:.3f}") # 현재 오차 출력
        pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
        note_position(df=df, value=pos)
        if now_x_pos - target_x_pos > 0: # x가 너무 나아감
            drone.set_pitch(-support_power)
            if now_y_pos - target_y_pos > 0: # y가 너무 나아감
                drone.set_roll(support_power)
                drone.move()
            elif now_y_pos - target_y_pos < 0: # y가 덜 나아감
                drone.set_roll(-support_power)
                drone.move()
            else: # y는 별 문제없음
                drone.set_roll(0)
                drone.move()
        elif now_x_pos - target_x_pos < 0: # x가 덜 나아감
            drone.set_pitch(support_power)
            if now_y_pos - target_y_pos > 0: # y가 너무 나아감
                drone.set_roll(support_power)
                drone.move()
            elif now_y_pos - target_y_pos < 0: # y가 덜 나아감
                drone.set_roll(-support_power)
                drone.move()
            else: # y는 별 문제없음
                drone.set_roll(0)
                drone.move()
        else: # x는 별 문제없음
            drone.set_pitch(0)
            if now_y_pos - target_y_pos > 0: # y가 너무 나아감
                drone.set_roll(support_power)
                drone.move()
            elif now_y_pos - target_y_pos < 0: # y가 덜 나아감
                drone.set_roll(-support_power)
                drone.move()
            else: # y는 별 문제없음
                break # x와 y 모두 오차가 0인 경우이므로 반복 종료
        time.sleep(TIME_DELAY)
        RMSE =  math.sqrt((now_x_pos - target_x_pos)**2 + (now_y_pos - target_y_pos)**2) # 오차 업데이트

    # 보정 종류
    drone.set_pitch(0)
    drone.set_roll(0)
    drone.move()
    print("보정 완료")
    pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
    note_position(df=df, value=pos)

    # 착륙
    drone.land()
    print("안전히 착륙 완료")
    pos = drone.get_pos_x(), drone.get_pos_y(), drone.get_pos_z()
    note_position(df=df, value=pos)

if __name__ == '__main__':
    drone = Drone()
    drone.pair()
    drone.takeoff()

    try:
        # 앞으로 곧장 전진 후 착륙(착륙 도중 보정)
        # go_straight(100)

        ## 드론을 반시계 방향으로 돌리기

        ## 보정 안한 버전
        go_to_pos_NoSupport(target_pos=(100, 0))
        go_to_pos_NoSupport(target_pos=(100, 100))
        go_to_pos_NoSupport(target_pos=(0, 100))
        go_to_pos_NoSupport(target_pos=(0, 0))
        # 깡 착륙
        drone.land()

        ## 보정한 버전
        # go_to_pos(target_pos=(100, 0), allow_RMSE=20)
        # go_to_pos(target_pos=(100, 100), allow_RMSE=20)
        # go_to_pos(target_pos=(0, 100), allow_RMSE=20)
        # go_to_pos(target_pos=(0, 0), allow_RMSE=20)

        # 보정 착륙
        # landing_assist(target_pos=(0, 0), allow_RMSE=5)
        
    except KeyboardInterrupt:
        print("\nCtrl + C 입력")
        drone.land() # 무조건 착륙
    finally: # 에러 여부와 관계없이 실행. 드론 페어링 문제를 예방하고 드론의 동작 데이터를 뽑아내기 위함
        drone.close()
        print("연결종료")

        df.to_csv(f'csv_files/mycsv_{int(time.time())}.csv', index=False, header=True, columns=['x_pos', 'y_pos', 'z_pos'])
        # index : 첫 열에 순서 인덱스(0, 1, 2, ...)을 담을 것이냐
        # header = 맨 첫 행에 각 열의 이름('x_pos'와 같은 것)을 포함시킬 것이냐, 새로운 이음을 줄 거라면 리스트로 정해주기
        # columns = 어떤 열만을 어떤 순서로 저장할 것이냐
