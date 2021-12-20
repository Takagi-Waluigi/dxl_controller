import os
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import * # Uses Dynamixel SDK library

class dxl_controller:
    def __init__(self, id1, id2):
        #Parameters for my dynamixel
        self.ADDR_OPERATING_MODE         = 11
        self.ADDR_TORQUE_ENABLE          = 64
        self.ADDR_GOAL_VELOCITY          = 104
        self.ADDR_GOAL_POSITION          = 116
        self.ADDR_PRESENT_POSITION       = 132
        self.DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
        self.DXL_MAXIMUM_POSITION_VALUE  = 4095      # Refer to the Maximum Position Limit of product eManual
        self.BAUDRATE                    = 115200
        self.PROTOCOL_VERSION            = 2.0
        self.DXL_ID_1                      = id1
        self.DXL_ID_2                      = id1
        self.TORQUE_ENABLE               = 1     # Value for enabling the torque
        self.TORQUE_DISABLE              = 0     # Value for disabling the torque
        self.DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold
        self.DEVICENAME                  = 'COM4'
        self.OperatingMode               = 1     # 0:Current 1:Velocity 3:Position
        self.index = 0
        self.dxl_goal_position = [self.DXL_MINIMUM_POSITION_VALUE, self.DXL_MAXIMUM_POSITION_VALUE]  

        self.portHandler = PortHandler(self.DEVICENAME)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        #Decide Operating Mode
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_1, self.ADDR_OPERATING_MODE, self.OperatingMode)

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_2, self.ADDR_OPERATING_MODE, self.OperatingMode)

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        # Enable Dynamixel Torque
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_1, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
        else:
            print("Dynamixel has been successfully connected")

        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_2, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
        else:
            print("Dynamixel has been successfully connected")

    def controllVelocity(self, id, vel):
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, id, self.ADDR_GOAL_VELOCITY, vel)

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))


    def controllPosition(self, id):
        #print("Press any key to continue! (or press ESC to quit!)")
        #if getch() == chr(0x1b):

        self.dxl_comm_result, self.dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, id, self.ADDR_GOAL_POSITION, self.dxl_goal_position[self.index])

        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        while 1:            
            self.dxl_present_position, self.dxl_comm_result, self.dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_PRESENT_POSITION)

            if self.dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
            elif self.dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
            
            if not abs(self.dxl_goal_position[self.index] - self.dxl_present_position) > self.DXL_MOVING_STATUS_THRESHOLD:
                break

        print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (id, 0, self.dxl_present_position))
        # Change goal position
        if self.index == 0:
            self.index = 1
        else:
            self.index = 0

    def release(self):
        # Disable Dynamixel Torque
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_1, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID_2, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))


        
        # Close port
        print("close port")
        self.portHandler.closePort()

