import math
import sys
import threading
import time
from typing import Optional
import rclpy
import serial
from rclpy.node import Node
from std_msgs.msg import Float32

BAUDRATE = 115200
SERIAL_READ_TIMEOUT_SEC = 0.2
PUBLISH_PERIOD_SEC = 1.0

MAX_FRAME_BYTES = 128
MAX_READ_CHUNK_BYTES = 4096
STALE_TIMEOUT_SEC = 2.5
SERIAL_IDLE_RECONNECT_TIMEOUT_SEC = 5.0
WARNING_THROTTLE_SEC = 0.5
RECONNECT_INITIAL_DELAY_SEC = 1.0
RECONNECT_MAX_DELAY_SEC = 5.0
MIN_TEMPERATURE_C = -50.0
MAX_TEMPERATURE_C = 200.0

class DrillSensorBridge(Node):
    def __init__(self, port_path: str) -> None:
        super().__init__("drill_sensor_bridge")

        self._port_path = port_path
        self._publisher = self.create_publisher(
            Float32,
            "/rover/drill/temperature",
            10,
        )

        self._latest_temperature: Optional[float] = None
        self._latest_temperature_time: Optional[float] = None
        self._temperature_lock = threading.Lock()

        self._stop_event = threading.Event()
        self._startup_time = time.monotonic()
        self._was_stale = False

        self._warning_lock = threading.Lock()
        self._last_warning_time = {}
        self._suppressed_warning_count = {}

        self._reader_thread = threading.Thread(
            target=self._serial_reader_loop,
            name="drill-uart-reader",
            daemon=True,
        )
        self._publish_timer = self.create_timer(
            PUBLISH_PERIOD_SEC,
            self._publish_latest_temperature,
        )
        self._reader_thread.start()

        self.get_logger().info(
            f"UART bridge started for port {self._port_path}. "
            f"Publication period: {PUBLISH_PERIOD_SEC:.1f} s."
        )

    def _warn_throttled(self, key: str, message: str) -> None:
        now = time.monotonic()
        should_log = False
        suppressed = 0

        with self._warning_lock:
            last = self._last_warning_time.get(key)
            if last is None or now - last >= WARNING_THROTTLE_SEC:
                self._last_warning_time[key] = now
                suppressed = self._suppressed_warning_count.pop(key, 0)
                should_log = True
            else:
                self._suppressed_warning_count[key] = (
                    self._suppressed_warning_count.get(key, 0) + 1
                )

        if should_log:
            if suppressed:
                message += f" ({suppressed} similar warnings suppressed)"
            self.get_logger().warning(message)

    def _serial_reader_loop(self) -> None:
        retry_delay = RECONNECT_INITIAL_DELAY_SEC
        has_connected_before = False

        while not self._stop_event.is_set() and rclpy.ok():
            try:
                with serial.Serial(
                    port=self._port_path,
                    baudrate=BAUDRATE,
                    timeout=SERIAL_READ_TIMEOUT_SEC,
                ) as serial_port:
                    if not has_connected_before:
                        self.get_logger().info(
                            f"Connected to serial port {self._port_path}."
                        )
                        has_connected_before = True
                    else:
                        self._warn_throttled(
                            "serial_reconnected",
                            f"Serial port {self._port_path} reconnected.",
                        )

                    retry_delay = RECONNECT_INITIAL_DELAY_SEC
                    self._read_serial_connection(serial_port)

            except (serial.SerialException, OSError) as exc:
                if not self._stop_event.is_set():
                    self._warn_throttled(
                        "serial_connection_error",
                        f"UART error on {self._port_path}: {exc}. "
                        f"Retrying in {retry_delay:.1f} s.",
                    )
            except Exception as exc:
                if not self._stop_event.is_set():
                    self._warn_throttled(
                        "unexpected_reader_error",
                        f"Unexpected UART reader error on {self._port_path}: "
                        f"{exc}. Retrying in {retry_delay:.1f} s.",
                    )

            if self._stop_event.is_set() or not rclpy.ok():
                break

            self._stop_event.wait(retry_delay)
            retry_delay = min(retry_delay * 2.0, RECONNECT_MAX_DELAY_SEC)

    def _read_serial_connection(self, serial_port: serial.Serial) -> None:
        frame_buffer = bytearray()
        discarding_oversized_frame = False
        last_rx_time = time.monotonic()

        while not self._stop_event.is_set() and rclpy.ok():
            waiting = serial_port.in_waiting
            bytes_to_read = min(waiting, MAX_READ_CHUNK_BYTES) if waiting else 1
            chunk = serial_port.read(bytes_to_read)
            if not chunk:
                if time.monotonic() - last_rx_time >= SERIAL_IDLE_RECONNECT_TIMEOUT_SEC:
                    raise serial.SerialException(
                        f"no UART bytes received for "
                        f"{SERIAL_IDLE_RECONNECT_TIMEOUT_SEC:.1f} s"
                    )
                continue

            last_rx_time = time.monotonic()

            for byte in chunk:
                if discarding_oversized_frame:
                    if byte == 0x0A:
                        discarding_oversized_frame = False
                    continue

                if byte == 0x0A:
                    raw_frame = bytes(frame_buffer) + b"\n"
                    frame_buffer.clear()
                    self._process_frame(raw_frame)
                    continue

                if len(frame_buffer) >= MAX_FRAME_BYTES - 1:
                    frame_buffer.clear()
                    discarding_oversized_frame = True
                    self._warn_throttled(
                        "oversized_frame",
                        f"Oversized UART frame on {self._port_path}. "
                        f"Discarding bytes until the next newline "
                        f"(limit {MAX_FRAME_BYTES} bytes).",
                    )
                    continue

                frame_buffer.append(byte)

    def _process_frame(self, raw_frame: bytes) -> None:
        try:
            frame = raw_frame.decode("ascii").strip()
        except UnicodeDecodeError:
            self._warn_throttled(
                "frame_encoding",
                f"Skipped UART frame with non-ASCII bytes: {raw_frame!r}",
            )
            return

        if not frame:
            return

        if not frame.startswith("TEMP:"):
            self._warn_throttled(
                "frame_format",
                f"Skipped malformed UART frame: {frame!r}."
            )
            return

        value_text = frame[len("TEMP:"):]
        try:
            temperature = float(value_text)
        except ValueError:
            self._warn_throttled(
                "frame_value",
                f"Skipped invalid temperature frame: {frame!r}",
            )
            return

        if not math.isfinite(temperature):
            self._warn_throttled(
                "non_finite_temperature",
                f"Skipped non-finite temperature: {frame!r}",
            )
            return

        if not MIN_TEMPERATURE_C <= temperature <= MAX_TEMPERATURE_C:
            self._warn_throttled(
                "temperature_out_of_range",
                f"Skipped temperature {temperature!r} °C; allowed range is "
                f"{MIN_TEMPERATURE_C}...{MAX_TEMPERATURE_C} °C."
            )
            return

        with self._temperature_lock:
            self._latest_temperature = temperature
            self._latest_temperature_time = time.monotonic()

    def _publish_latest_temperature(self) -> None:
        now = time.monotonic()

        with self._temperature_lock:
            temperature = self._latest_temperature
            received_at = self._latest_temperature_time

        if temperature is None or received_at is None:
            if now - self._startup_time > STALE_TIMEOUT_SEC:
                self._was_stale = True
                self._warn_throttled(
                    "no_valid_reading",
                    "No valid temperature has been received yet. "
                    "Publishing is paused until a valid frame arrives.",
                )
            return

        age = now - received_at
        if age > STALE_TIMEOUT_SEC:
            self._was_stale = True
            self._warn_throttled(
                "stale_reading",
                f"Last valid temperature is {age:.1f} s old. "
                "Skipping publication until fresh data arrives.",
            )
            return

        if self._was_stale:
            self.get_logger().info("Fresh temperature data received again.")
            self._was_stale = False

        message = Float32()
        message.data = temperature

        try:
            self._publisher.publish(message)
        except Exception as exc:
            self._warn_throttled(
                "publish_error",
                f"Could not publish temperature: {exc}",
            )

    def destroy_node(self):
        self._stop_event.set()

        if self._reader_thread.is_alive():
            self._reader_thread.join(timeout=2.0)
            if self._reader_thread.is_alive():
                self._warn_throttled(
                    "reader_shutdown_timeout",
                    "UART reader thread did not stop within 2 seconds."
                )

        return super().destroy_node()


def main() -> int:
    if len(sys.argv) < 2:
        print(
            f"Usage: python3 {sys.argv[0]} <serial_port_path>",
            file=sys.stderr,
        )
        return 2

    port_path = sys.argv[1]
    rclpy.init(args=[])
    node = None

    try:
        node = DrillSensorBridge(port_path)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
