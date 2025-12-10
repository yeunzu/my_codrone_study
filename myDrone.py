from codrone_edu.drone import *
import pandas as pd
from myCodroneLibrary import MyCodrone 
# myCodroneLibrary.py에 정의한 클래스를 모듈로 불러와 라이브러리인 것처럼 쓰게 만들었음
# 이러는 편이 실제 드론 조작에 있어 편리하기 때문
# 복잡한 드론 조작 로직은 가리고, 드론의 움직임 명령은 별도의 공간에서 간편하게 하는 것이 편할테니.

drone = Drone()
drone.pair()

df = pd.DataFrame(columns=["times", "x_pos", "y_pos", "z_pos"])

try:
    myDrone = MyCodrone(drone=drone, df=df, save_logFile_directory="logs")
    myDrone.drone.takeoff()
    myDrone.logger.info("드론 이륙")

    myDrone.set_height(150)

    x, y = 351, -506
    myDrone.go_direct(target_pos=(x, y), speed=51, allow_error=3, decrease_speed_zone_range=80, decreased_speed=20)
    myDrone.landing_assist(stop_z_pos=15, allow_error=5, target_pos=(x, y), land_speed=35, support_power=30)

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

## 참고 : 배터리 80% 언저리일 때 가장 깔끔