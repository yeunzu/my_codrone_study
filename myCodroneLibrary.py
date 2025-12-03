from codrone_edu.drone import *
import pandas as pd
import time
import math
from collections.abc import Iterable
import warnings
import logging

class MyCodrone:
    def __init__(
            self, 
            drone: Drone, 
            df: pd.DataFrame,
            time_delay: int | float = 0.1,
            save_logFile_directory: str = "", 
            save_logFile_fileName: str = f"log_{int(time.time())}"
            ):
        ## 기본 값 & 객체 초기화
        self.drone = drone
        self.df = df
        self.TIME_DELAY = time_delay
        self.SYSTEM_START_TIME = time.time()


        ## MyCodrone 객체 생성 시 실행될 기능들
        self.drone.position_data = [0, 0, 0, 0] # 객체 생성과 동시에 드론 위치 데이터 초기화

        logger = logging.getLogger() # 로그를 위한 객체 생성
        logger.setLevel(logging.DEBUG) # INFO 이상의 로그를 출력
        # 참고 : logging의 로그 수준 우선순위는 아래외 같다.
        # CRITICAL > ERROR > WARNING > INFO > DEBUG (왼쪽으로 갈 수록 우선순위가 높음)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") # 로그 출력 형식

        # 콘솔에 출력할 로그 설정
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 로그 파일을 통한 경로 설정
        current_file_path = os.path.abspath(__file__) # 현재 파이썬 파일 실행시점의 절대경로 획득
        root_directory = os.path.dirname(current_file_path) # 파일 경로에서 디렉터리 경로만 추출
        log_directory = os.path.join(root_directory, save_logFile_directory) # 로그 디렉터리의 절대 경로 생성
        log_file_path = os.path.join(log_directory, f'{save_logFile_fileName}.log') # 로그 파일의 최종 경로 생성
        os.makedirs(log_directory, exist_ok=True) # 로그 디렉터리가 없으면 생성, exist_ok=True 옵션으로 디렉터리가 이미 존재할 경우에 생기는 경고 생략

        # 로그 파일에 출력할 로그 출력
        file_handler = logging.FileHandler(filename=log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self.logger = logger
        

    def note_position(
            self, 
            value: Iterable
            ):
        '''
        ## 현재 위치를 기록하는 함수
        DataFrame의 맨 마지막 부분에 입력된 값(value)를 추가하는 것. value는 print()로 출력된다.
        '''
        # 예외처리
        if len(self.df.columns)-1 != len(value):
            self.logger.error(f"DataFrame의 열 개수와 value의 원소 개수가 맞지 않습니다.\n\tDataFrame의 열 개수(시간 제외): {len(self.df.columns)-1}\n\tvalue의 원소 개수: {len(value)}")
            raise ValueError(f"DataFrame의 열 개수와 value의 원소 개수가 맞지 않습니다.\n\tDataFrame의 열 개수(시간 제외): {len(self.df.columns)-1}\n\tvalue의 원소 개수: {len(value)}")
        # 예외처리

        # print(value)
        value = list(value) # 리스트화
        value = [time.time() - self.SYSTEM_START_TIME] + value # 시간 경과 값 추가
        self.logger.info(f"저장되는 값: {value}")
        try:
            self.df.loc[len(self.df)] = value
        except Exception as e:
            self.logger.error("note_position() 함수에서 에러 발생", exc_info=True)
            self.logger.error(f"{type(e).__name__}")
            self.logger.error(f"\t{e}")
            raise

    def save_csv(
            self, 
            csv_path: str = '',
            csv_fileName: str = ''
    ):
        current_path = os.path.abspath(__file__) # 현재 파이썬 파일의 절대 경로
        root_directory = os.path.dirname(current_path)
        csv_directory = os.path.join(root_directory, csv_path)
        csv_file_path = os.path.join(csv_directory, f'{csv_fileName}.csv')
        os.makedirs(csv_directory, exist_ok=True)
        self.df.to_csv(csv_file_path, index=False, header=True)
        # index : 첫 열에 순서 인덱스(0, 1, 2, ...)을 담을 것이냐
        # header = 맨 첫 행에 각 열의 이름('x_pos'와 같은 것)을 포함시킬 것이냐, 새로운 이음을 줄 거라면 리스트로 정해주기
        # columns = 어떤 열만을 어떤 순서로 저장할 것이냐)


    def go_to_pos(
            self, 
            target_pos: Iterable = (0, 0), 
            allow_error: float | int = 5, 
            decrease_speed_zone_range : float | int = 15, 
            speed: int = 20,
            decreased_speed: int = 10
    ):
        '''
        ## 드론을 원하는 좌표까지 옮겨주는 함수
        : 드론 동체의 회전 없이 드론을 원하는 좌표로 이동시킵니다.

        ### 파라미터 설명
        - target_pos : 오로지 두 개의 원소(각 원소는 int 혹은 float)만을 가지는 iterable을 받습니다. 앞에서부터 순서대로 x, y를 의미합니다.
        - allow_error : 허용 오차 범위. 목표 좌표를 기준으로 오차 범위만큼 x, y 평면에 원을 그린다고 가정할 때, 드론이 해당 원 안에 들어온다면 목표 좌표(target_pos)에 도달했다고 판단합니다. 아래의 deceased_speed_zone_range보단 값의 크기가 반드시 작아야 합니다.
        - decrease_speed_zone_range : 감속 보정 구간. 속도를 줄여 허용 오차 범위 안으로 들어가기 위한 보정을 시작할 범위를 지정합니다. 위의 allow_error보단 값의 크기가 반드시 커야 합니다.
        - speed : 드론의 속도를 조절합니다. 0보다 크고 100 이하인 정수만을 받습니다.
        - decreased_speed : 감속 보정 구간에서 드론이 움직일 속도입니다.
        '''
        ## 예외처리
        if len(target_pos) != 2: # target_pos의 원소 개수가 2개가 아니면 ValueError
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
            raise ValueError(f"go_to_pos() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
        
        for i in range(2): # target_pos를 순회하며 값을 검사
            value = target_pos[i]
            if ((type(value) != type(0)) and (type(value) != type(0.))): # target_pos로 받은 원소 2개가 int나 float가 아니면 TypeError
                if (type(value) == type("ㅗ")): # 다만 원소가 문자열이면 실수로 변환하고 경고를 띄움
                    target_pos[i] = float(value) # 실수로 바꾼 값을 해당 인덱스에 저장
                    self.logger.warning("go_to_pos() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.")
                    warnings.warn("go_to_pos() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.", RuntimeWarning)
                else: # 원소가 문자열조차도 아니면 TypeError
                    self.logger.error(f"TypeError\n\tgo_to_pos() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t해당 값의 타입: {type(value)}\n\t문제가 되는 값의 인덱스: {i}")
                    raise TypeError(f"go_to_pos() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t해당 값의 타입: {type(value)}\n\t문제가 되는 값의 인덱스: {i}")
        if not (allow_error < decrease_speed_zone_range):
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 allow_error와 decrease_speed_zone_range는 다음 관계를 반드시 만족해야 합니다. \tallow_error < decrease_speed_zone_range")
            raise ValueError(f"ValueError\n\tgo_to_pos() 함수에서 allow_error와 decrease_speed_zone_range는 다음 관계를 반드시 만족해야 합니다. \tallow_error < decrease_speed_zone_range")

        if not (0 < speed <= 100):
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 speed: {speed}")
            raise ValueError(f"go_to_pos() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 speed: {speed}")
        # 예외 처리

        self.logger.debug("go_to_pos() 함수 시작")
        self.logger.debug("입력된 인자: ")
        self.logger.debug(f"\ttarget_pos: {target_pos} \tallow_error: {allow_error} \tspeed: {speed}")

        # 좌표 확인
        target_x, target_y = target_pos
        now_x, now_y = self.drone.get_pos_x(), self.drone.get_pos_y()
        self.logger.debug(f"\tnow_pos(x, y): {(now_x, now_y)}")

        distence = lambda now_x, now_y, target_x, target_y: math.sqrt((target_x - now_x)**2 + (target_y - now_y)**2) # 거리 계산 함수

        # 1단계. 일단 오차 처리 없이 쭉 가기
        # x 먼저
        self.logger.info("일단 오차 보정 없이 이동")
        while (target_x - now_x > 0) and (distence(now_x, now_y, target_x, target_y) > decrease_speed_zone_range): # 앞으로 가야 하는 경우
            self.drone.set_pitch(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            # 좌표 업데이트
            now_x, now_y = pos_data[0], pos_data[1]
        self.drone.reset_move_values()
        self.drone.move()
        
        while (target_x - now_x < 0) and (distence(now_x, now_y, target_x, target_y) > decrease_speed_zone_range): # 뒤로 가야 하는 경우
            self.drone.set_pitch(-speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            # 좌표 업데이트
            now_x, now_y = pos_data[0], pos_data[1]
        self.drone.reset_move_values()
        self.drone.move()

        # x 움직인 이후 y 움직이기
        while (target_y - now_y > 0) and (distence(now_x, now_y, target_x, target_y) > decrease_speed_zone_range): # 왼쪽으로 가야 하는 경우
            self.drone.set_roll(-speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            # 좌표 업데이트
            now_x, now_y = pos_data[0], pos_data[1]
        self.drone.reset_move_values()
        self.drone.move()

        while (target_y - now_y < 0) and (distence(now_x, now_y, target_x, target_y) > decrease_speed_zone_range): # 오른쪽으로 가야 하는 경우
            self.drone.set_roll(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            # 좌표 업데이트
            now_x, now_y = pos_data[0], pos_data[1]
        self.drone.reset_move_values()
        self.drone.move()

        ## 2단계. 허용오차 안까지 느린 속도로 접근하기
        ## 이제부턴 x와 y를 동시에 움직임
        ## 이 움직임은 (감속구간)&(허용오차구간^(C))에서 작용. 즉, 감속 구간 안이지만, 오차를 허용하는 구간
        while (allow_error < distence(now_x, now_y, target_x, target_y) <= decrease_speed_zone_range + 3): # 속도 감속 구간 범위에 3을 더한 것은 약간의 오차를 커버하기 위함
            # 일단 현재 데이터 기록, 좌표 업데이트부터
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            now_x, now_y = pos_data[0], pos_data[1]
            self.logger.info(f"목표와의 오차: {distence(now_x, now_y, target_x, target_y)}cm")
            # x변화, y변화
            x_diff = target_x - now_x
            y_diff = target_y - now_y
            # arctan을 이용해 각도 구하기
            theta = math.atan2(y_diff, x_diff)
            # pitch_power(앞뒤 움직임), roll_power(좌우 움직임) 계산 <- 삼각함수 이용
            pitch_power = decreased_speed * math.cos(theta)
            roll_power = decreased_speed * math.sin(theta)
            # 연산이 올바른지 확인하기 위한 디버깅 로그
            self.logger.debug(f"pitch_power: {pitch_power} \troll_power: {roll_power}")
            self.logger.debug(f"pitch_power^2 + roll_power^2 = {pitch_power**2 + roll_power**2}")
            self.logger.debug(f"decreased_speed^2 = {decreased_speed**2}")
            self.logger.debug(f"is pitch_power^2 + roll_power^2 == decreased_speed^2 -> {int(pitch_power**2 + roll_power**2) == int(decreased_speed**2)}")
            # pitch, roll 설정 및 움직임
            self.drone.set_pitch(pitch_power)
            self.drone.set_roll(-roll_power) # 이상하게 y좌표는 좌표상의 부호와, set_roll 함수 인자의 부하가 뒤집어져있어 부호를 바꿔줌
            self.drone.move()
            time.sleep(self.TIME_DELAY)

        # 이동 정보 초기화
        self.drone.reset_move_values()
        self.drone.move()
        # print("지정한 좌표까지 이동완료")
        self.logger.info("지정한 좌표로 이동완료")
        # 데이터 기록
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        

    def set_height(
            self, 
            target_z: int | float,
            speed: int = 25
    ):
        '''
        ## 드론의 고도(높이)를 조절하는 함수
        - target_z : 목표하는 z좌표(즉, cm단위의 높이)를 정수 혹은 실수의 형태로 받습니다. 다만 그 값은 0보다 커야 합니다.
        - speed: 드론의 고도 조절 시의 속도를 받습니다. 0보다 크고 100 이하인 정수를 받습니다.
        '''
        ## 예외처리
        if not target_z > 0: # 목표 z가 0보다 크지 않다면 ValueError
            self.logger.error(f"ValueError\n\tset_height() 함수에서 target_z 값은 0보다 커야 합니다.\n\t입력된 target_z의 값: {target_z}")
            raise ValueError(f"ValueError\n\tset_height() 함수에서 target_z 값은 0보다 커야 합니다.\n\t입력된 target_z의 값: {target_z}")
        if not 0 < speed <= 100: # 속도가 0보다 크고 100 이하의 범위에 들어있지 않다면
            self.logger.error(f"ValueError\n\tset_height() 함수에서 speed 값은 0보다 크고 100 이하이어야 합니다.\n\t입력된 speed의 값: {speed}")
            raise ValueError(f"ValueError\n\tset_height() 함수에서 speed 값은 0보다 크고 100 이하이어야 합니다.\n\t입력된 speed의 값: {speed}")
        ## 예외처리

        # 데이터 기록 & 현재 좌표 추출
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        now_z = pos_data[-1]

        self.logger.info(f"드론 고도 조정\n\t현재 고도: {now_z}\t목표 고도: {target_z}")

        while abs(now_z) - abs(target_z) < 0: # 현재 고도가 목표 고도보다 낮은 경우
            self.logger.info("고도 상승 진행 중")
            self.drone.set_throttle(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            now_z = pos_data[-1]
        self.drone.reset_move_values()
        self.drone.move()

        while abs(now_z) - abs(target_z) > 0: # 현재 고도가 목표 고도보다 높은 경우
            self.logger.info("고도 하강 진행 중")
            self.drone.set_throttle(-speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            now_z = pos_data[-1]
        self.drone.reset_move_values()
        self.drone.move()
        
        self.logger.info(f"고도 조정 완료: \n\t목표 고도: {target_z}\t도달 목표: {now_z}")


    def turn_body(
            self, 
            target_angle: float | int
    ):
        '''
        ## 드론의 몸체를 회전하는 함수
        - TODO: 드론을 회전시키는 함수를 찾지 못해 미완성
        '''
        self.drone.info("turn_body() 함수는 아직 미완성입니다.")
        pass

    def landing_assist(
            self, 
            stop_z_pos: float | int = 12, 
            target_pos: Iterable = (0, 0), 
            allow_error: float | int = 3, 
            land_speed: float | int = 30, 
            support_power: float | int = 8
    ): 
        '''
        ## 착륙을 보조하는 함수
        : 원하는 위치(target_pos)까지의 착륙을 허용 오차(allow_error) 이내로 이뤄지게끔 합니다.
        1. z으로 12cm(기본값, stop_z_pos 값으로 수정 가능) 위까지 빠르게 낙하합니다. 이때 낙하 속도는 land_speed로 조절 가능합니다.
        2. 이후 x, y축을 보정한 후 착륙합니다.
        3. target_pos는 순서대로 x, y 좌표를 의미하는 두 개의 정수 혹은 실수의 원소로 이뤄진 iterable이어야 합니다.
        4. support_power는 z축 12cm 즈음에서 x, y축 위치를 보정할 때의 드론의 움직임 속도를 조절하는 인자입니다. 
        '''
        ## 예외처리
        if len(target_pos) != 2: # target_pos의 원소 개수가 2개가 아니면 ValueError
            self.logger.error(f"ValueError\n\tlanding_assist() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
            raise ValueError(f"landing_assist() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
        
        for i in range(2): # target_pos를 순회하며 값을 검사
            value = target_pos[i]
            if ((type(value) != type(0)) and (type(value) != type(0.))): # target_pos로 받은 원소 2개가 int나 float가 아니면 TypeError
                if (type(value) == type("ㅗ")): # 다만 원소가 문자열이면 실수로 변환하고 경고를 띄움
                    target_pos[i] = float(value) # 실수로 바꾼 값을 해당 인덱스에 저장
                    self.logger.warning("landing_assist() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.")
                    warnings.warn("landing_assist() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.", RuntimeWarning)
                else: # 원소가 문자열조차도 아니면 TypeError
                    self.logger.error(f"TypeError\n\tlanding_assist() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t문제가 되는 값의 인덱스: {i}")
                    raise TypeError(f"landing_assist() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t문제가 되는 값의 인덱스: {i}")
               
        if not (0 < land_speed <= 100):
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 land_speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 land_speed: {land_speed}")
            raise ValueError(f"landing_assist() 함수에서 land_speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 land_speed: {land_speed}")

        if not (0 < support_power <= 100):
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 support_power는 0보다 크고 0 이하인 정수이어야 합니다.\n\t입력된 support_power: {support_power}")
            raise ValueError(f"landing_assist() 함수에서 support_power는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 support_power: {support_power}")
        ## 예외처리

        self.logger.info("착륙 시작")
        target_x, target_y = target_pos
        
        # 데이터 기록
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        now_x, now_y, now_z = pos_data

        distence = lambda now_x, now_y, target_x, target_y: math.sqrt((target_x - now_x)**2 + (target_y - now_y))
        now_distence = distence(now_x, now_y, target_x, target_y)

        # # 오차가 허용치의 3배 이상이면 착륙 중단
        # if now_distence >= 5*allow_error:
        #     self.logger.warning("목표 x, y 좌표와의 거리가 허용 오차의 5배 이상입니다. 보정이 이뤄지는 착륙은 취소됩니다.")
        #     self.logger.warning(f"허용 오차: {allow_error} \t현재 오차: {now_distence}")
        #     return # 함수 탈출
        
        # 목표 높이까지 착륙 시작
        while now_z > stop_z_pos:
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            self.drone.set_throttle(-land_speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            now_z = pos_data[2]

        self.logger.info("목표 고도까지 하강완료")
        self.drone.reset_move_values()
        self.drone.move()

        self.logger.info("보정 시작")
        ## go_to_pos() 함수의 2단계 보정 시스템을 그대로 응용
        while distence(now_x, now_y, target_x, target_y) > allow_error: # 
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            now_x, now_y, now_z = pos_data
            x_diff = target_x - now_x
            y_diff = target_y - now_y
            theta = math.atan2(y_diff, x_diff)
            pitch_power = support_power * math.cos(theta)
            roll_power = support_power * math.sin(theta)
            # 연산이 올바른지 확인하기 위한 디버깅 로그
            self.logger.debug(f"pitch_power: {pitch_power} \troll_power: {roll_power}")
            self.logger.debug(f"pitch_power^2 + roll_power^2 = {pitch_power**2 + roll_power**2}")
            self.logger.debug(f"decreased_speed^2 = {support_power**2}")
            self.logger.debug(f"is pitch_power^2 + roll_power^2 == decreased_speed^2 -> {int(pitch_power**2 + roll_power**2) == int(support_power**2)}")
            # 드론 값 설정
            self.drone.set_pitch(pitch_power)
            self.drone.set_roll(-roll_power)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
        
        # 움직임 초기화
        self.drone.reset_move_values()
        self.drone.move()
        # 완전 착륙 직전 데이터 기록
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        self.drone.land()
        # 완전 착륙 이후 데이터 기록
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        self.logger.info("드론 착륙 완료")
        self.logger.info(f"최종 착륙 좌표: {(pos_data[0], pos_data[1])}")





if __name__ == '__main__':
    drone = Drone()
    drone.pair()

    df = pd.DataFrame(columns=["times", "x_pos", "y_pos", "z_pos"])
    try:
        myDrone = MyCodrone(drone=drone, df=df, save_logFile_directory="logs")
        
        myDrone.drone.takeoff()
        myDrone.logger.info("드론 이륙")
        # myDrone.set_height(120)
        allow_err = 4
        low_speed_zone = 10
        spt_pwr = 4
        myDrone.go_to_pos(target_pos=(100, 0), allow_error=allow_err, decrease_speed_zone_range=low_speed_zone, decreased_speed=spt_pwr)
        myDrone.go_to_pos(target_pos=(100, 100), allow_error=allow_err, decrease_speed_zone_range=low_speed_zone, decreased_speed=spt_pwr)
        myDrone.go_to_pos(target_pos=(0, 100), allow_error=allow_err, decrease_speed_zone_range=low_speed_zone, decreased_speed=spt_pwr)
        # 마지막에 착륙 지점으로 올 때에는 오차 최소화를 위해 시작부터 느린 속도로...
        myDrone.go_to_pos(target_pos=(0, 20), speed=10, allow_error=allow_err, decrease_speed_zone_range=low_speed_zone, decreased_speed=spt_pwr-2)
        myDrone.go_to_pos(target_pos=(0, 0), speed=8, allow_error=2, decrease_speed_zone_range=8, decreased_speed=spt_pwr-2)
        # myDrone.drone.land()
        myDrone.landing_assist(stop_z_pos=15, allow_error=2, target_pos=(0, 0), land_speed= 25, support_power=4)
    except KeyboardInterrupt:
        myDrone.logger.warning("Ctrl+C 입력")
        drone.land()
    except Exception as e:
        myDrone.logger.error("에러 발생")
        myDrone.logger.error(f"{type(e).__name__}", exc_info=True)
        myDrone.logger.error(f"\t{e}")
        drone.land()
        raise
    finally:
        myDrone.logger.info("드론 착륙 후 연결 해제")
        drone.close()
        myDrone.save_csv(csv_path='csvs', csv_fileName=f'csv_{int(time.time())}')
        myDrone.logger.info("csv 저장 완료")