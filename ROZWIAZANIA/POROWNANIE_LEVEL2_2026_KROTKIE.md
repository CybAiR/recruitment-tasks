# CybAiR · Rekrutacja 2026 — Level 2

Porównanie pięciu implementacji mostu UART → ROS 2. Wszystkie pięć zgłoszeń mają status rekrutacyjny **Zaliczone**. [Zestawienie rozwiązań](README.md)

## Wyniki CORE i STRESS

CORE sprawdza wymagania zadania, a STRESS weryfikuje działanie przy zmiennej częstotliwości ramek UART od 2 do 50 Hz. [Kontrakt Level 2](../01_DLA_REKRUTOW/README.md#2-specyfikacja-techniczna-kontrakt-api)

| Implementacja | Rewizja | CORE | STRESS |
|:--|:--|:--:|:--:|
| [Igor Górnik · PR #1](https://github.com/CybAiR/recruitment-tasks/pull/1) | `ef88c75` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Dominik Kotus · PR #2](https://github.com/CybAiR/recruitment-tasks/pull/2) | `7d46434` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Dawid Bilski · PR #3](https://github.com/CybAiR/recruitment-tasks/pull/3) | `91437ba` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Yahor Hrykhutsik · PR #6](https://github.com/CybAiR/recruitment-tasks/pull/6) | `5f9cafc` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |
| [Denys Denysenko · PR #7](https://github.com/CybAiR/recruitment-tasks/pull/7) | `2d38092` | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) |

W STRESS dla każdej z pięciu implementacji odebrano **32 wiadomości** ROS 2 ze średnim tempem około **1 Hz**. W porównaniu z danymi UART wykryto **0 niezgodnych i 0 zaległych próbek**. Po każdej z **16 błędnych ramek** odebrano poprawny pomiar z nowszej ramki.

## Architektura i próby EXTENDED

| Obszar | Igor Górnik | Dominik Kotus | Dawid Bilski | Yahor Hrykhutsik | Denys Denysenko |
|:--|:--|:--|:--|:--|:--|
| Odczyt UART | Osobny wątek i blokada stanu pomiaru | Nieblokujący odczyt z timera co 10 ms i wydzielony parser | Nieblokujący odczyt z timera co 20 ms i walidacja w funkcji odczytu | Nieblokujący odczyt dostępnych bajtów z timera co 10 ms | Nieblokujący odczyt z timera co 20 ms, do 4096 B na odczyt, z wydzielonym parserem |
| Dłuższa cisza na UART · EXTENDED | Wstrzymał publikację. W kodzie próg wieku ostatniego poprawnego pomiaru wynosi 2,5 s. | Powtarzał ostatni poprawny pomiar. | Powtarzał ostatni poprawny pomiar. | Powtarzał ostatni poprawny pomiar. | Powtarzał ostatni poprawny pomiar. |
| Odłączenie portu · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — wznowił pomiary po podmianie PTY | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — proces zakończył się błędem wejścia/wyjścia | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — proces zakończył się błędem wejścia/wyjścia | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — proces zakończył się błędem wejścia/wyjścia | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — po podmianie PTY nadal publikował ostatni pomiar |
| Zbyt długa ramka · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił całą ramkę | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z końcówki ramki | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z końcówki ramki | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę |
| Dodatkowy dwukropek · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wartość z pola przed dodatkowym dwukropkiem | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił ramkę |
| `NaN`, `+Inf`, `−Inf` · EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił 3/3 | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił 3/3 | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił 3/3 | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował wszystkie trzy | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — odrzucił 3/3 |
| Zakres `Float32` (`1e39`) · próba dodatkowa | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — zachował pomiar, ostrzegł | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) — zachował pomiar, ostrzegł | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował `+Inf` | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował `+Inf` | ![FAIL](https://img.shields.io/badge/status-FAIL-red) — opublikował `+Inf` |
| Wynik zbiorczy EXTENDED | ![PASS](https://img.shields.io/badge/status-PASS-brightgreen) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) | ![FAIL](https://img.shields.io/badge/status-FAIL-red) |
| Metryki · scenariusze EXTENDED (PASS / FAIL) | 9 / 0 | 7 / 2 | 6 / 3 | 7 / 2 | 8 / 1 |
| Metryki · STRESS (maks. odstęp odbioru / mediana opóźnienia ROS 2) | 1,0007 s / 0,51 ms | 1,0008 s / 0,45 ms | 1,0006 s / 0,52 ms | 1,0010 s / 0,52 ms | 1,0011 s / 0,51 ms |

Wynik zbiorczy i licznik EXTENDED obejmują dziewięć standardowych scenariuszy. W próbie `NaN`, `+Inf` i `−Inf` odrzucenie oznaczało zachowanie ostatniego poprawnego pomiaru i ostrzeżenie po każdej ramce. Wartość `1e39` jest skończona i przekracza zakres `Float32`. Sprawdzono ją w dodatkowej próbie. Przyjęcie ramki z dodatkowym dwukropkiem przez implementację Dawida odbiega od wymaganego formatu `TEMP:<float>\n`.

Opóźnienie ROS 2 oszacowano od znacznika czasu nadania RMW do odbioru przez subskrybenta.

## Zakres pomiarów

Testy wykonano **21 listopada 2026 r.** dla trzech implementacji i **28 listopada 2026 r.** dla wszystkich pięciu (55 prób). Oba przebiegi wykonano w Dockerze z **ROS 2 Jazzy** i wirtualnym portem szeregowym **PTY**. Tempo ROS 2 oszacowano z odstępów między odbiorami wiadomości. Pomiary dotyczą wyłącznie plików `serial_bridge_node.py` we wskazanych rewizjach i warunków emulowanego łącza.

Wyniki prób mają status **VERIFIED (synthetic/harness)**, a opis odczytu UART — **VERIFIED (code audit)**.
