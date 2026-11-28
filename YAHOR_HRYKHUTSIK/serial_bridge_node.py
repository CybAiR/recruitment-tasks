import serial
import rclpy
from rclpy.node import Node
import sys
from std_msgs.msg import Float32

class DrillSensorBridge(Node):
    def __init__(self):
        super().__init__('drill_sensor_bridge')
        port=sys.argv[1]
        self.serial=serial.Serial(port, 115200, timeout=0)
        self.get_logger().info(f'Connected to serial port: {port}')
        self.buffer = b''
        self.latest_temperature = None

        self.publisher = self.create_publisher(Float32,'/rover/drill/temperature',10)

        self.read_timer = self.create_timer(0.01 , self.read_serial)
        self.publish_timer = self.create_timer(1, self.publish_temperature)

    def read_serial(self):
        if self.serial.in_waiting > 0: 
           data = self.serial.read(self.serial.in_waiting)
           self.buffer += data
           while b'\n' in self.buffer:
                 line, self.buffer = self.buffer.split(b'\n', 1)
                 try:
                     text = line.decode('utf-8')
                     if not text:
                         continue
                 except UnicodeDecodeError:
                     self.get_logger().warning('Invalid frame: cannot decode bytes')
                     continue
                 if text.startswith('TEMP:'):
                    value = text[5:]
                    try: 
                        temperature = float(value)
                        self.latest_temperature = temperature
                    except ValueError:
                           self.get_logger().warning(f'Invalid temperature frame: {text}')
                 else:
                     self.get_logger().warning(f'Unknown frame: {text}')

    def publish_temperature(self):
        if self.latest_temperature is not None:
           msg=Float32()
           msg.data = self.latest_temperature
           self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DrillSensorBridge()
    try:
        rclpy.spin(node)
    finally:
        node.serial.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
