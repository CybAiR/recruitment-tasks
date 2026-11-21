
import sys
import math
import serial
import rclpy

from rclpy.node import Node
from std_msgs.msg import Float32


def parse_temperature(frame: bytes) -> float | None:
    try:
        text = frame.decode("utf-8").strip()

        if not text.startswith("TEMP:"):
            return None

        temperature = float(text[5:])

        if not math.isfinite(temperature) or abs(temperature) > 3.4028234663852886e38:
            return None

        return temperature

    except (ValueError, UnicodeDecodeError):
        return None


class DrillSensorBridge(Node):

    def __init__(self, port):
        super().__init__("drill_sensor_bridge")

        self.publisher = self.create_publisher(
            Float32,
            "/rover/drill/temperature",
            10
        )

        self.latest_valid_temperature = None
        self.rx_buffer = bytearray()

        self.uart = serial.Serial(
            port,
            baudrate=115200,
            timeout=0
        )

        self.read_timer = self.create_timer(
            0.01, self.read_uart
        )

        self.publish_timer = self.create_timer(
            1.0, self.publish_temperature
        )

        self.get_logger().info(f"Port UART: {port}")

    def read_uart(self):
        available = self.uart.in_waiting

        if available == 0:
            return

        data = self.uart.read(min(available, 4096))
        self.rx_buffer.extend(data)

        while True:
            end = self.rx_buffer.find(b"\n")

            if end == -1:
                break

            frame = bytes(self.rx_buffer[:end + 1])
            del self.rx_buffer[:end + 1]

            temperature = parse_temperature(frame)

            if temperature is None:
                self.get_logger().warning(
                    f"Bledna ramka: {frame!r}"
                )
            else:
                self.latest_valid_temperature = temperature

        if len(self.rx_buffer) > 4096:
            self.get_logger().warning(
                "Zbyt dluga ramka - czyszczenie bufora"
            )
            self.rx_buffer.clear()

    def publish_temperature(self):
        if self.latest_valid_temperature is None:
            return

        msg = Float32()
        msg.data = self.latest_valid_temperature

        self.publisher.publish(msg)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Blad: podaj sciezke do portu szeregowego.\n"
            "Skladnia: python3 serial_bridge_node.py <PORT>\n"
        )

    port = sys.argv[1]

    rclpy.init(args=[])
    node = None

    try:
        node = DrillSensorBridge(port)
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.uart.close()
            node.destroy_node()

        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
