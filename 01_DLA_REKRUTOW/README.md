# Zadanie Rekrutacyjne (Level 2): Most UART -> ROS2


> **Dla bardziej zaawansowanych:**
> [Level 3 – Sterowanie ramieniem robotycznym w ROS 2](LEVEL_3.md)

---

## 1. Cel zadania
Stworzenie węzła ROS2 (Black-Box) w pliku **`serial_bridge_node.py`**, który odbiera surowe dane z wirtualnego portu szeregowego (symulującego mikrokontroler wiertła), odfiltrowuje błędy transmisji i publikuje pomiar w sieci ROS2.

---

## 2. Specyfikacja techniczna (Kontrakt API)

Twój skrypt **`serial_bridge_node.py`** musi spełniać poniższe wymagania:

1. **Parametryzacja wejścia:** Przyjmuje ścieżkę do portu szeregowego jako pierwszy argument linii poleceń (`sys.argv[1]`), np. `python3 serial_bridge_node.py /dev/pts/1`. Wpisywanie portu na sztywno w kodzie (hardcoding) dyskwalifikuje rozwiązanie.
2. **Format ramek UART:** Poprawna ramka ma postać `TEMP:<float>\n` (np. `TEMP:34.2\n`). Na linii mogą pojawiać się uszkodzone ramki (np. `TEMP:ERR_CRC_FAIL\n`) – węzeł musi je zignorować, zalogować ostrzeżenie (self.get_logger().warning()). i działać dalej bez awarii (crashu).
3. **Separacja częstotliwości (Decoupling):** Fizyczny czujnik na łaziku może nadawać ze zmienną, wysoką częstotliwością (np. 10–50 Hz). Twój węzeł musi na bieżąco opróżniać bufor portu szeregowego (nie blokując pętli `rclpy.spin`), ale **publikować najświeższą poprawną wartość na topic ROS2 ze stałą częstotliwością 1.0 Hz (raz na sekundę)**.
4. **Wyjście ROS2:**
   * Nazwa węzła: `drill_sensor_bridge`
   * Topic: `/rover/drill/temperature`
   * Typ wiadomości: `std_msgs/msg/Float32`

---

## 3. Uruchomienie środowiska Docker (Krok po kroku)

Wszystkie operacje wykonujemy wewnątrz kontenera Dockerowego z ROS2 Jazzy (Ubuntu 24.04). Ze względu na izolację jądra Linuksa, wirtualne porty `/dev/pts/X` są widoczne tylko wewnątrz tego samego kontenera.

### Przygotowanie obrazu (jednorazowo):
W głównym folderze repozytorium (gdzie znajduje się `Dockerfile` oraz `sensor_mock_basic.py`) zbuduj obraz:

```bash
docker build -t cybair_ros2 .
```

### Testowanie rozwiązania (na 3 terminalach):

**Terminal 1 (Start kontenera i symulatora):**
1. Uruchom kontener z podmontowanym bieżącym katalogiem:
   ```bash
   docker run -it --rm --name ros2_test -v $(pwd):/workspace cybair_ros2 bash
   ```
2. Uruchom symulator i odczytaj wygenerowany port (np. `/dev/pts/1`):
   ```bash
   python3 sensor_mock_basic.py
   ```

**Terminal 2 (Uruchomienie Twojego węzła):**
1. W nowym oknie terminala podepnij się do działającego kontenera:
   ```bash
   docker exec -it ros2_test bash
   ```
2. Załaduj środowisko ROS2 i uruchom swój skrypt z portem z Terminala 1:
   ```bash
   source /opt/ros/jazzy/setup.bash
   python3 IMIE_NAZWISKO/serial_bridge_node.py /dev/pts/1
   ```

**Terminal 3 (Samokontrola w sieci ROS2):**
1. Podepnij się trzecim terminalem do kontenera:
   ```bash
   docker exec -it ros2_test bash
   source /opt/ros/jazzy/setup.bash
   ```
2. Sprawdź, czy dane pojawiają się na topicu:
   ```bash
   ros2 topic echo /rover/drill/temperature
   ```
3. Sprawdź, czy częstotliwość publikacji wynosi wymagane 1.0 Hz:
   ```bash
   ros2 topic hz /rover/drill/temperature
   ```

---

## 4. Procedura oddania zadania (Git Flow & Pull Request)

Nie modyfikuj plików w głównym katalogu repozytorium. Obowiązuje standardowy proces Code Review:

1. Sklonuj to repozytorium (lub zrób `Fork`, jeśli nie masz jeszcze uprawnień zapisu do organizacji) i utwórz własnego brancha roboczego:
   ```bash
   git checkout -b zadanie/imie-nazwisko
   ```
2. W głównym katalogu repozytorium utwórz folder nazwany swoim imieniem i nazwiskiem (bez polskich znaków i spacji, wielkimi literami), np.:
   ```text
   JAN_KOWALSKI/
   └── serial_bridge_node.py
   ```
3. Umieść swój kod wyłącznie wewnątrz swojego folderu (`IMIE_NAZWISKO/serial_bridge_node.py`). Nie commituj plików tymczasowych (`__pycache__`, logów itp.).
4. Wypchnij swojego brancha na GitHuba:
   ```bash
   git add IMIE_NAZWISKO/serial_bridge_node.py
   git commit -m "Dodanie rozwiazania Level 2: Imie Nazwisko"
   git push origin zadanie/imie-nazwisko
   ```
5. Na GitHubie otwórz **Pull Request (PR)** do gałęzi `main` tego repozytorium:
   * **Tytuł PR:** `[Level 2] Imię Nazwisko`
   * **Reviewers:** Przypisz mnie (**`@Konstanty-K`**) jako osobę sprawdzającą (Reviewer).
Kod zostanie poddany przeglądowi (Code Review) oraz zweryfikowany automatycznym stress-testem (zmienna częstotliwość nadawania UART + zakłócenia).
