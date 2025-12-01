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


    def go_straight(
            self, 
            length: float | int, 
            speed: int = 20
            ):
        '''
        ## 드론을 앞으로 이동시키는 함수
        : 드론을 원하는 거리만큼 앞으로 이동시킵니다. 보다 정확히는 드론을 x좌표 상에서 이동시킵니다.

        ### 파라미터 설명
        - length: 앞으로 갈 거리를 cm 단위로 받습니다.
        - speed: 드론의 속도를 조정합니다. 기본값은 20이며, 0보다 크고 100 이하인 정수를 받습니다.
        '''
        # 예외처리
        if not (0 < speed <= 100):
            raise ValueError(f"go_straight() 함수에서 speed는 0보다 크고 100 이하인 정수(int)만 허용됩니다.\n\t입력된 speed: {speed}\n\t입력된 speed의 type: {type(speed)}")
        # 예외처리

        start_x = self.drone.get_pos_x() # 이동 시작 전 드론의 x좌표를 기록해둡니다.
        # print(f"앞으로 {length}cm 이동 시작")
        self.logger.info(f"앞으로 {length}cm 이동 시작")

        if length >= 0: # 주어진 거리가 0보다 큰, 즉 앞으로 가는 명령이라면
            self.drone.set_pitch(speed)
        else: # 주어진 거리가 0보다 작은, 즉 뒤로 가는 명령이라면
            self.drone.set_pitch(-speed)

        now_x = self.drone.get_pos_x() # 드론의 현재 x좌표 받음
        moved_length = abs(now_x - start_x) # 거리 차이를 저장

        # 거리차이가 이동 길이 이하인 경우 반복
        while moved_length <= abs(length):
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)

            self.drone.move() # 앞서 설정된 pitch 값으로 이동

            time.sleep(self.TIME_DELAY) # 반복문에 딜레이 주기

        # 이동 완료 -> 이동 정보 초기화
        self.drone.reset_move_values()
        self.drone.move() # 초기화된 이동 정보를 반영 (혹시 모를 상황을 방지하기 위해 move()를 사용)
        # print("앞으로 이동 종료")
        self.logger.info("앞으로 이동 종료")


    def go_to_pos(
            self, 
            target_pos: Iterable = (0, 0), 
            allow_error: float | int = 5, 
            speed: int = 20
    ):
        '''
        ## 드론을 원하는 좌표까지 옮겨주는 함수
        : 드론 동체의 회전 없이 드론을 원하는 좌표로 이동시킵니다.

        ### 파라미터 설명
        - target_pos : 오로지 두 개의 원소(각 원소는 int 혹은 float)만을 가지는 iterable을 받습니다. 앞에서부터 순서대로 x, y를 의미합니다.
        - allow_error : 허용할 오차 범위입니다. 목표 좌표를 기준으로 오차 범위만큼 x, y 평면에 원을 그린다고 가정할 때, 드론이 해당 원 안에 들어온다면 목표 좌표(target_pos)에 도달했다고 판단합니다.
        - speed : 드론의 속도를 조절합니다. 0보다 크고 100 이하인 정수만을 받습니다.
        '''
        ## 예외처리
        if len(target_pos) != 2: # target_pos의 원소 개수가 2개가 아니면 ValueError
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
            raise ValueError(f"go_to_pos() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
        
        # for i in range(2): # target_pos를 순회하며 값을 검사
        #     value = target_pos[i]
        #     if ((type(value) != type(0)) or (type(value) != type(0.))): # target_pos로 받은 원소 2개가 int나 float가 아니면 TypeError
        #         if (type(value) == type("ㅗ")): # 다만 원소가 문자열이면 실수로 변환하고 경고를 띄움
        #             target_pos[i] = float(value) # 실수로 바꾼 값을 해당 인덱스에 저장
        #             self.logger.warning("go_to_pos() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.")
        #             warnings.warn("go_to_pos() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.", RuntimeWarning)
        #         else: # 원소가 문자열조차도 아니면 TypeError
        #             self.logger.error(f"TypeError\n\tgo_to_pos() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t해당 값의 타입: {type(value)}\n\t문제가 되는 값의 인덱스: {i}")
        #             raise TypeError(f"go_to_pos() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t해당 값의 타입: {type(value)}\n\t문제가 되는 값의 인덱스: {i}")
                
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

        # x_error, y_error = abs(now_x) - abs(target_x), abs(now_y) - abs(target_y)
        now_error = math.sqrt((now_x - target_x)**2 + (now_y - target_y)**2)
        self.logger.debug(f"연산된 현재 오차: {now_error}")

        # x 먼저 이동
        # print("x 이동 중")
        self.logger.info("x 먼저 이동 중")

        now_error, previous_error = now_error, now_error
        set_speed = speed

        while now_error > allow_error: # 오차가 허용치 초과한다면
            self.logger.debug("오차가 허용치를 초과함")
            # 데이터 기록
            try:
                self.logger.debug("좌표 데이터 기록")
                pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
                self.note_position(pos_data)
            except Exception as e:
                self.logger.error("오차가 허용치를 초과해 조정하기 위해 데이터를 기록하려던 중 에러 발생")
                self.logger.error(f"{type(e).__name__}")
                self.logger.error(f"\t{e}")
                raise

            # 좌표 정보 확보
            self.logger.debug("좌표 정보 확보")
            now_x, now_y = pos_data[0], pos_data[1]
            self.drone.set_roll(0) # 좌우는 가만히

            # 오차의 변화 경향 파악
            self.logger.debug("오차 변화 경향 파악")
            if previous_error - now_error >= 0: # 과거 오차에 비해 현재 오차가 적어짐 -> 오차가 줄어드는 경향
                self.logger.debug("오차가 줄어드는 경향")
                set_speed = set_speed # 그대로 유지
            else: # 과거 오차에 비해 현재 오차가 커짐 -> 오차가 커지는 경향 -> 반대로 움직여줘소 오차를 잡아줘야 함
                self.logger.debug("오차가 늘아나는 경향")
                set_speed = -set_speed # 반대로 움직이게끔 부호 반전

            self.drone.set_pitch(set_speed)
                
            # if now_x - target_x <0: # x가 앞으로 진행할 때 덜 나아갔거나, 뒤로 진행할 때 더 많이 나간 경우
            #     self.drone.set_pitch(speed)
            # else: # x가 양의 방향으로 더 나아갔거나, 음의 방향으로 덜 나아간 경우
            #     self.drone.set_pitch(-speed)

            self.drone.move()
            self.logger.debug("드론 움직이고 딜래이")
            time.sleep(self.TIME_DELAY)

            # 오차 업데이트
            now_x, now_y = self.drone.get_pos_x(), self.drone.get_pos_y()
            # x_error, y_error = abs(now_x) - abs(target_x), abs(now_y) - abs(target_y)
            self.logger.debug("오차 업데이트 전")
            self.logger.debug(f"\tprevious_error: {previous_error} \tnow_error: {now_error}")
            previous_error = now_error
            now_error = math.sqrt((now_x - target_x)**2 + (now_y - target_y)**2)
            self.logger.debug("오차 업데이트 후")
            self.logger.debug(f"\tprevious_error: {previous_error} \tnow_error: {now_error}")
            self.logger.info(f"현재 오차: {now_error}")
            
            if now_error <= allow_error:# 오차가 허용치 이내로 들어온다면 반복문 종료
                break

        # Y 이동
        # print("y 이동 중")
        self.logger.info("y 이동 중")
        while now_error > allow_error: # 오차가 허용치를 초과한다면
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)

            # 좌표 정보 확보
            now_x, now_y = pos_data[0], pos_data[1]
            self.drone.set_pitch(0) #앞뒤는 가만히

            # if now_y - target_y < 0: # y가 왼쪽으로 진행할 때 덜 나아갔거나, 오른쪽으로 진행할 때 더 나아간 경우
            #     self.drone.set_roll(-speed)
            # else: # y가 왼쪽으로 진행할 때 더 나아갔거나, 오른쪽으로 진행할 때 덜 나아간 경우
            #     self.drone.set_roll(speed)

            if previous_error - now_error > 0: # 과거 오차에 비해 현재 오차가 적어짐 -> 오차가 줄어드는 경향
                set_speed = set_speed
            else: # 과거 오차에 비해 현재 오차가 커짐 -> 오차가 커지는 경향 -> 반대로 움직여줘소 오차를 잡아줘야 함
                set_speed = -set_speed # 반대로 움직이게끔 부호 반전
            self.drone.set_roll(set_speed)

            self.drone.move()
            time.sleep(self.TIME_DELAY)

            # 오차 업데이트
            now_x, now_y = self.drone.get_pos_x(), self.drone.get_pos_y()
            # x_error, y_error = abs(now_x) - abs(target_x), abs(now_y) - abs(target_y)
            previous_error = now_error
            now_error = math.sqrt((now_x - target_x)**2 + (now_y - target_y)**2)
            self.logger.info(f"현재 오차: {now_error}")

            if now_error <= allow_error:# 오차가 허용치 이내로 들어온다면 반복문 종료
                break

        # 이동 정보 초기화
        self.drone.reset_move_values()
        self.drone.move()
        # print("지정한 좌표까지 이동완료")
        self.logger.info("지정한 좌표로 이동완료")
        # 데이터 기록
        pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
        self.note_position(pos_data)
        

    def go_to_pos_NoSupport(
            self, 
            target_pos: Iterable = (0, 0), 
            speed: int = 20
    ):
        '''
        ### 드론을 원하는 좌표까지 옮겨주는 함수
        드론 동체의 회전 없이 드론을 원하는 좌표로 이동시킵니다.
        좌표에 도달하면 동작을 멈추는 단순한 동작만을 합니다. 별도의 오차범위를 고려하지 않습니다.
        - target_pos : 오로지 두 개의 원소(각 원소는 int 혹은 float)만을 가지는 iterable을 받습니다. 앞에서부터 순서대로 x, y를 의미합니다.
        - speed : 드론의 속도를 조정합니다. 0 < speed <= 100의 정수만 받습니다.
        '''
        ## 예외처리
        if len(target_pos) != 2: # target_pos의 원소 개수가 2개가 아니면 ValueError
            self.logger.error(f"ValueError\n\tgo_to_pos() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
            raise ValueError(f"go_to_pos_NoSupport() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
        
        for i in range(2): # target_pos를 순회하며 값을 검사
            value = target_pos[i]
            if ((type(value) != type(0)) or (type(value) != type(0.))): # target_pos로 받은 원소 2개가 int나 float가 아니면 TypeError
                if (type(value) == type("ㅗ")): # 다만 원소가 문자열이면 실수로 변환하고 경고를 띄움
                    target_pos[i] = float(value) # 실수로 바꾼 값을 해당 인덱스에 저장
                    self.logger.warning("go_to_pos_NoSupport() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.")
                    warnings.warn("go_to_pos_NoSupport() 함수에서 target_pos의 원소는 문자열을 받을 수 없습니다. 따라서 자체적으로 실수로 변환해 사용합니다. 이 경우, 값에 이상이 생길 가능성이 있습니다.", RuntimeWarning)
                else: # 원소가 문자열조차도 아니면 TypeError
                    self.logger.error(f"TypeError\n\tgo_to_pos_NoSupport() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t문제가 되는 값의 인덱스: {i}")
                    raise TypeError(f"go_to_pos_NoSupport() 함수에서 target_pos의 원소는 오로지 정수 혹은 실수만을 받을 수 있습니다.\n\t문제가 되는 원소 값: {value}\n\t문제가 되는 값의 인덱스: {i}")
                
        if not (0 < speed <= 100):
            self.logger.error(f"ValueError\n\tgo_to_pos_NoSupport() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 speed: {speed}")
            raise ValueError(f"go_to_pos_NoSupport() 함수에서 speed는 0보다 크고 100 이하인 정수이어야 합니다.\n\t입력된 speed: {speed}")
        ## 예외처리

        now_x, now_y = self.drone.get_pos_x(), self.drone.get_pos_y()
        target_x, target_y = target_pos

        while abs(now_x) < abs(target_x): # 원점 기준으로, 현재 x 거리가 목표 x 거리보다 짧은 경우
            self.logger.info("+x 방향으로 이동")
            if abs(abs(target_x) - abs(now_x)) < 1: # x축 방향 초과가 1 이내면 반복 깨기
                break
            self.drone.set_pitch(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
        self.drone.reset_move_values()
        self.drone.move()

        while abs(now_x) > abs(target_x): # 원점 기준으로, 현재 x 거리가 목표 x 거리보다 긴 경우
            self.logger.info("-x 방향으로 이동")
            if abs(abs(now_x) - abs(target_x)) < 1: # x축 방향 초과가 1 이내면 반복 깨기
                break
            self.drone.set_pitch(-speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)

            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
        self.drone.reset_move_values()
        self.drone.move()

        while abs(now_y) < abs(target_y): # 원점 기준으로, 현재 y 거리가 목표 y 거리보다 긴 경우
            self.logger.info("-y 방향으로 이동")
            if abs(abs(target_y) - abs(now_y)) < 1: # y축 방향 초과가 1 이내면 반복 깨기
                break
            self.drone.set_roll(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)

            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
        self.drone.reset_move_values()
        self.drone.move()

        while abs(now_y) > abs(target_y):
            self.logger.info("+y 방향으로 이동")
            if abs(abs(now_y) - abs(target_y)) < 1: # y축 방향 초과가 1 이내면 반복 깨기
                break
            self.drone.set_roll(speed)
            self.drone.move()
            time.sleep(self.TIME_DELAY)
            
            # 데이터 기록
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
        self.drone.reset_move_values()
        self.drone.move()

        self.logger.info("지정한 좌표까지 보정 없이 이동완료")
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
        
        ## 주의사항
        - 이 함수는 착륙하고자 하는 좌표(target_pos) 기준 허용 오차(allow_error)보다 3배 이상 먼 거리에 있는 경우엔 경고를 띄우며 착륙을 시행하지 않습니다. 지면에 거의 붙어있다시피 한 상태에서의 비행은 드론의 정상적인 비행이라고 보기 어려우며, 지면의 장애물에 의한 드론의 손상이 발생할 위함이 있기 때문입니다.
    
        '''
        ## 예외처리
        if len(target_pos) != 2: # target_pos의 원소 개수가 2개가 아니면 ValueError
            self.logger.error(f"ValueError\n\tlanding_assist() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
            raise ValueError(f"landing_assist() 함수에서 target_pos는 정수 혹은 실수의 오로지 2개의 원소를 가지는 iterable이어야 합니다.\n\t입력된 target_pos: {target_pos}\n\ttarget_pos의 원소의 개수: {len(target_pos)}")
        
        for i in range(2): # target_pos를 순회하며 값을 검사
            value = target_pos[i]
            if ((type(value) != type(0)) or (type(value) != type(0.))): # target_pos로 받은 원소 2개가 int나 float가 아니면 TypeError
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
        now_z = pos_data[-1]
        
        # 목표 높이까지 착륙 시작
        while now_z > stop_z_pos:
            pos_data = self.drone.get_pos_x(), self.drone.get_pos_y(), self.drone.get_pos_z()
            self.note_position(pos_data)
            self.drone.set_throttle(-land_speed)





if __name__ == '__main__':
    drone = Drone()
    drone.pair()

    df = pd.DataFrame(columns=["times", "x_pos", "y_pos", "z_pos"])
    try:
        myDrone = MyCodrone(drone=drone, df=df, save_logFile_directory="logs")
        
        myDrone.drone.takeoff()
        myDrone.logger.info("드론 이륙")
        # myDrone.set_height(120)
        myDrone.go_to_pos(target_pos=(100, 0))
        myDrone.go_to_pos(target_pos=(100, 100))
        myDrone.go_to_pos(target_pos=(0, 100))
        myDrone.go_to_pos(target_pos=(0, 0))
        myDrone.drone.land()
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