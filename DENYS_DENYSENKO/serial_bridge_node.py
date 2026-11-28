import sys   
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import serial
import math

class DrillSensorBridge(Node):
    def __init__(self, port:str, frame_length:int = 4096): 
        super().__init__('drill_sensor_bridge')
        self.publisher_ = self.create_publisher(Float32, '/rover/drill/temperature', 10)
        
        self.read_timer = self.create_timer(0.02, self.read_uart)
        self.publisher_timer = self.create_timer(1.0, self.publish_temperature)
        
        self.latest_valid_temperature = None
        self.buffer = bytearray()
        self.frame_length = frame_length
        self.uart = None
        
        # UART setup
        try:
            self.uart = serial.Serial(port=port, baudrate=115200, timeout=0)
            self.get_logger().info(f"Podlaczono do {port}.")
        except serial.SerialException as e:
            self.get_logger().error(f"Nie udalo sie otworzyc port: {e}")
            return
        
    def read_uart(self) -> None:
        if self.uart is None or not self.uart.is_open:
            return
        
        try: 
            waiting = self.uart.in_waiting
            data = self.uart.read(min(waiting, self.frame_length))
            self.buffer.extend(data)
        except (serial.SerialException, OSError) as e:
            self.get_logger().error(f"Blad odczytu z portu szeregowego: {e}")
            return
            
        while True:
            line_index = self.buffer.find(b'\n')
            if line_index == -1:
                break
            line = bytes(self.buffer[:line_index + 1])
            del self.buffer[:line_index + 1]
            self.process_frame(line)
            
    def process_frame(self, line) -> None:
        text = line.decode('utf-8', errors='replace').strip()
        # Sprawdzamy format TEMP:<float>
        prefix, sep, raw_value = text.partition(':')
        if sep != ':' or prefix != 'TEMP' or not raw_value:
            self.get_logger().warning(f"Odrzucono niepoprawną ramkę: '{text}'")
            return

        try:
            value = float(raw_value)
        except ValueError:
            self.get_logger().warning(f"Odrzucono ramkę z błędną wartością: '{text}'")
            return

        # Odrzucamy NaN oraz +/-Inf
        if not math.isfinite(value):
            self.get_logger().warning(f"Odrzucono nieskończoną lub NaN wartość: '{text}'")
            return

        self.latest_valid_temperature = value
        
        
    def publish_temperature(self) -> None:
        if self.latest_valid_temperature is None:
            self.get_logger().warning("Brak poprawnego odczytu temperatury.")
            return
        
        msg = Float32()
        msg.data = self.latest_valid_temperature
        self.publisher_.publish(msg)
        self.get_logger().info(f'Temperatura: {msg.data:.2f}')

def main(args = None):
    if len(sys.argv) != 2:
        print("Nie podano portu szeregowego.")
        return
        
    port = sys.argv[1]
    frame_length = 4096
    rclpy.init(args=args)
    drill_sensor_bridge = None
    
    try:
        drill_sensor_bridge = DrillSensorBridge(port, frame_length)
        rclpy.spin(drill_sensor_bridge)
    except KeyboardInterrupt:
        pass
    finally:
        if drill_sensor_bridge is not None:
            drill_sensor_bridge.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    
if __name__ == '__main__':
    main()