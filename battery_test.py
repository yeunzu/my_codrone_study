from codrone_edu.drone import *

drone = Drone()
drone.pair()
print(drone.get_battery())
drone.close()