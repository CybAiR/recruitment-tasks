# Zadanie rekrutacyjne (Level 3): Sterowanie ramieniem robotycznym w ROS 2

## 1. Cel zadania

Stworzenie prostego systemu sterowania wirtualnym ramieniem robotycznym, wykorzystującego komunikację pomiędzy węzłami ROS 2.

Możliwość sterowania ramieniem z poziomu terminala, a efekty widoczne w RViz 2.

Zadanie ma charakter otwarty — sposób implementacji oraz wybór modelu robota pozostają po stronie uczestnika.

## 2. Wymagania

1. **Model ramienia:** Wykorzystaj dowolny model manipulatora robotycznego (zalecany 6-DOF). Możesz skorzystać z gotowego modelu URDF.

2. **Wizualizacja:** Uruchom model ramienia w ROS 2 i wyświetl go w RViz 2.

3. **Sterowanie:** Przygotuj interfejs umożliwiający wprowadzanie komend ruchu z osobnego terminala. Może to być sterowanie strzałkami, klawiszami WASD, komendami tekstowymi lub inne rozwiązanie.

4. **Komunikacja ROS 2:** Komendy sterujące muszą być publikowane na topicu ROS 2 i odbierane przez osobny węzeł (Publisher → Subscriber).

5. **Reakcja ramienia:** Węzeł sterujący powinien przetwarzać otrzymane komendy i aktualizować konfigurację przegubów. Zmiany powinny być widoczne na bieżąco w RViz 2.


Można korzystać z gotowych modeli, bibliotek i pakietów ROS 2.

**Język:** Python lub C++.

## 3. Zakres zadania

Do wykonania zadania wystarczy realizacja wymagań opisanych w punkcie 2.

Nie wymagamy implementacji kinematyki odwrotnej, planowania ruchu ani symulacji fizyki. Osoby zainteresowane mogą samodzielnie rozszerzyć rozwiązanie, ale nie jest to konieczne.

Zadanie ma na celu sprawdzenie podstawowych umiejętności pracy z ROS 2. Po jego wykonaniu planujemy przejść do konkretnych projektów związanych z łazikiem, których zakres zostanie omówiony na spotkaniu sekcji.

## 4. Przydatne materiały

- [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)
- [RViz 2](https://github.com/ros2/rviz)
- [Robotics Toolbox for Python](https://github.com/petercorke/robotics-toolbox-python) – materiały pomocnicze dotyczące modelowania i kinematyki manipulatorów.
- [MoveIt 2](https://moveit.picknik.ai/)

## 5. Oddanie zadania

Umieść własny kod i niezbędne pliki konfiguracyjne w folderze `IMIE_NAZWISKO/` na własnym branchu i otwórz Pull Request do gałęzi `main`.

Możesz korzystać z gotowych modeli URDF i pakietów ROS 2. Nie musisz umieszczać w repozytorium dużych plików modeli 3D — wystarczy wskazać źródło wykorzystanego modelu.

W przypadku realizacji obu poziomów zadania umieść rozwiązania w osobnych podfolderach.

**Na spotkaniu sekcji pokaż na swoim laptopie, jak działa Twoje rozwiązanie.** Nie trzeba przygotowywać slajdów ani formalnej prezentacji.

**Jeżeli zadanie nie jest jeszcze ukończone, również możesz pokazać dotychczasowe postępy** — to, co już działa, oraz ewentualne problemy, na które natrafiłeś.

W przypadku pokazywania częściowo ukończonego zadania nie musisz wcześniej otwierać Pull Requesta.

## 6. Uwagi

Nie wymagamy symulacji fizyki ani integracji z rzeczywistym manipulatorem. Wystarczy kinematyczna wizualizacja ruchu w RViz 2.

Jeżeli rozpocząłeś już realizację własnej koncepcji sterowania ramieniem, możesz ją kontynuować. Nie musisz stosować dokładnie przedstawionej architektury, pod warunkiem że projekt realizuje główne założenia zadania, w szczególności komunikację między węzłami ROS 2 i sterowanie modelem manipulatora.