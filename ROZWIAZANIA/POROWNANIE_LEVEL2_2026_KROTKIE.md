# CybAiR · Rekrutacja 2026 — Level 2

Porównanie trzech implementacji mostu UART → ROS 2. Wszystkie trzy zgłoszenia mają status rekrutacyjny **Zaliczone**. [Zestawienie rozwiązań](README.md)

## Wyniki CORE i STRESS

CORE sprawdza wymagania zadania, a STRESS weryfikuje działanie przy zmiennej częstotliwości ramek UART od 2 do 50 Hz. [Kontrakt Level 2](../01_DLA_REKRUTOW/README.md#2-specyfikacja-techniczna-kontrakt-api)

| Implementacja | Rewizja | CORE | STRESS |
|:--|:--|:--:|:--:|
| [Igor Górnik · PR #1](https://github.com/CybAiR/recruitment-tasks/pull/1) | `ef88c75` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Dominik Kotus · PR #2](https://github.com/CybAiR/recruitment-tasks/pull/2) | `7d46434` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Dawid Bilski · PR #3](https://github.com/CybAiR/recruitment-tasks/pull/3) | `91437ba` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |

W STRESS dla każdej implementacji odebrano **32 wiadomości** ROS 2 ze średnim tempem około **1 Hz**. W porównaniu z danymi UART wykryto **0 niezgodnych i 0 zaległych próbek**. Po każdej z **16 błędnych ramek** odebrano poprawny pomiar z nowszej ramki.

## Architektura i próby EXTENDED

| Obszar | Igor Górnik | Dominik Kotus | Dawid Bilski |
|:--|:--|:--|:--|
| Odczyt UART | Osobny wątek i blokada stanu pomiaru | Nieblokujący odczyt z timera co 10 ms i wydzielony parser | Nieblokujący odczyt z timera co 20 ms i walidacja w funkcji odczytu |
| Dłuższa cisza na UART · EXTENDED | Wstrzymał publikację. W kodzie próg wieku ostatniego poprawnego pomiaru wynosi 2,5 s. | Powtarzał ostatni poprawny pomiar. | Powtarzał ostatni poprawny pomiar. |
| Odłączenie portu · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — wznowił pomiary po podmianie PTY | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — proces zakończył się błędem wejścia/wyjścia | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — proces zakończył się błędem wejścia/wyjścia |
| Zbyt długa ramka · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił całą ramkę | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z końcówki ramki | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z końcówki ramki |
| Dodatkowy dwukropek · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z pola przed dodatkowym dwukropkiem |
| Wynik zbiorczy EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) |

Statusy EXTENDED odnoszą się do kryteriów poszczególnych prób. Przyjęcie ramki z dodatkowym dwukropkiem przez implementację Dawida odbiega od wymaganego formatu `TEMP:<float>\n`. To odstępstwo wykryto w EXTENDED.

## Zakres pomiarów

Testy wykonano **21 listopada 2026 r.** w Dockerze z **ROS 2 Jazzy** i wirtualnym portem szeregowym **PTY**. Tempo ROS 2 oszacowano z odstępów między odbiorami wiadomości. Pomiary dotyczą wyłącznie plików `serial_bridge_node.py` we wskazanych rewizjach i warunków emulowanego łącza.
