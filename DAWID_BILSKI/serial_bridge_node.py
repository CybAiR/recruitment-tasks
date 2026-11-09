
import serial
import sys
import math
import rclpy
from std_msgs.msg import Float32

port_name = sys.argv[1]
ser = serial.Serial(port_name, 9600, timeout=0)

rclpy.init()
node = rclpy.create_node('drill_sensor_bridge')
publisher = node.create_publisher(Float32, '/rover/drill/temperature', 10)

najnowsza_temperatura = None
bufor = bytearray()

def czytaj_uart():
    global najnowsza_temperatura

    bufor.extend(ser.read(ser.in_waiting))

    while b'\n' in bufor:
        indeks = bufor.index(b'\n')
        ramka = bytes(bufor[:indeks])
        del bufor[:indeks + 1]

        line = ramka.decode('utf-8', errors='replace').strip()

        try:
            if not line.startswith('TEMP:'):
                raise ValueError

            temperatura = float(line.split(':')[1])

            if not math.isfinite(temperatura):
                raise ValueError

            najnowsza_temperatura = temperatura

        except ValueError:
            node.get_logger().warning('Bledna ramka: ' + line)

    if len(bufor) > 1024:
        bufor.clear()
        node.get_logger().warning('Za dluga ramka UART')

def wyslij():
    if najnowsza_temperatura is not None:
        msg = Float32()
        msg.data = najnowsza_temperatura
        publisher.publish(msg)
        node.get_logger().info(f'Temperatura: {msg.data}')

node.create_timer(0.02, czytaj_uart)
node.create_timer(1.0, wyslij)

try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    ser.close()
    node.destroy_node()
    rclpy.shutdown()

