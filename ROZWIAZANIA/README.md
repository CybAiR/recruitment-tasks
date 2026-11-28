# Rozwiązania rekrutacyjne CybAiR

Archiwum rozwiązań przesłanych w ramach rekrutacji.

| Uczestnik | Pull Request | Level 2 |
|---|---|---|
| Dawid Bilski | [#3](https://github.com/CybAiR/recruitment-tasks/pull/3) | Zaliczone |
| Denys Denysenko | [#7](https://github.com/CybAiR/recruitment-tasks/pull/7) | Zaliczone |
| Dominik Kotus | [#2](https://github.com/CybAiR/recruitment-tasks/pull/2) | Zaliczone |
| Igor Górnik | [#1](https://github.com/CybAiR/recruitment-tasks/pull/1) | Zaliczone |
| Yahor Hrykhutsik | [#6](https://github.com/CybAiR/recruitment-tasks/pull/6) | Zaliczone |

## Porównanie implementacji

[Level 2 — wyniki i porównanie techniczne pięciu implementacji (2026)](POROWNANIE_LEVEL2_2026_KROTKIE.md)

## Zakres weryfikacji

Automatyczne testy zadania Level 2 (UART → ROS 2) wykonano w Dockerze
z ROS 2 Jazzy i wirtualnym portem szeregowym PTY. Przebieg z 21 listopada
2026 r. objął PR-y #1–#3. W przebiegu z 28 listopada 2026 r. sprawdzono
PR-y #6 i #7 oraz ponownie uruchomiono testy dla PR-ów #1–#3.

Wszystkie pięć rozwiązań zaliczyło testy CORE i STRESS.

Formalna weryfikacja obejmowała wyłącznie plik
`serial_bridge_node.py` każdego uczestnika.

Dodatkowy symulator Dominika oraz rozwiązanie Level 3
Igora nie były przedmiotem formalnej oceny.

## Struktura

- `DAWID_BILSKI/` — rozwiązanie Level 2
- `DENYS_DENYSENKO/` — rozwiązanie Level 2
- `DOMINIK_KOTUS/` — rozwiązanie Level 2 i symulator
- `IGOR_GORNIK/zad2/` — rozwiązanie Level 2
- `IGOR_GORNIK/zad3/` — dodatkowe rozwiązanie Level 3
- `YAHOR_HRYKHUTSIK/` — rozwiązanie Level 2

Kod uczestników zachowano bez zmian.
