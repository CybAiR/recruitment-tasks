
import argparse
import os
import pty
import time


BAD_FRAMES = [
    b"TEMP:ERR_CRC_FAIL\n",
    b"TEMP:nan\n",
    b"TEMP:inf\n",
    b"TEMP:1e100\n",
    b"WRONG:32.5\n",
    b"TEMP:\n",
    b"\xff\xfe\n",
]


def make_frame(number):
    temperature = 20.0 + (number % 300) / 10
    return f"TEMP:{temperature:.1f}\n".encode("utf-8")


def send(master, data):
    while data:
        written = os.write(master, data)
        data = data[written:]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=["normal", "corrupted", "fragmented", "burst", "long"],
        default="normal"
    )

    parser.add_argument("--rate", type=float, default=5.0)
    args = parser.parse_args()

    if not 0 < args.rate <= 200:
        parser.error("--rate musi byc w zakresie (0, 200]")

    master, slave = pty.openpty()
    port = os.ttyname(slave)

    print(f"PORT: {port}", flush=True)
    print(f"TEST: {args.scenario}", flush=True)
    print(f"RATE: {args.rate} Hz (normal/corrupted/fragmented)")
    print("Zatrzymanie: Ctrl+C\n", flush=True)

    counter = 0

    try:
        while True:
            start = time.monotonic()

            if args.scenario == "burst":
                payload = b"".join(
                    make_frame(counter + i) for i in range(20)
                )
                send(master, payload)
                counter += 20
                print(f"[BURST] 20 ramek, ostatnia: {make_frame(counter - 1)!r}")
                time.sleep(0.5)
                continue

            if args.scenario == "long":
                send(master, b"X" * 5000)
                time.sleep(0.3)
                send(master, b"\n")
                send(master, make_frame(counter))
                print("[LONG] 5000 bajtow bez konca ramki + poprawna ramka")
                counter += 1
                time.sleep(1)
                continue

            frame = make_frame(counter)

            if args.scenario == "corrupted" and counter % 4 == 3:
                frame = BAD_FRAMES[(counter // 4) % len(BAD_FRAMES)]

            if args.scenario == "fragmented":
                for part in (frame[:3], frame[3:7], frame[7:]):
                    send(master, part)
                    time.sleep(0.01)
            else:
                send(master, frame)

            if counter % 10 == 0 or args.scenario == "corrupted":
                print(f"[TX] {frame!r}", flush=True)

            counter += 1

            elapsed = time.monotonic() - start
            time.sleep(max(0, 1.0 / args.rate - elapsed))

    except KeyboardInterrupt:
        print("\nSymulator zatrzymany.")

    finally:
        os.close(master)
        os.close(slave)


if __name__ == "__main__":
    main()

