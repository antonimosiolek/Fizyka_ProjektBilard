# 🎱 Billiard Chaos Simulation

Symulacja bilardu napisana w języku **Python** z wykorzystaniem biblioteki **Pygame**. Projekt został przygotowany w ramach zajęć z fizyki i demonstruje zastosowanie mechaniki klasycznej oraz metod numerycznych do modelowania ruchu ciał.

Głównym celem projektu jest jakościowa prezentacja **efektu motyla** (czułości na warunki początkowe) w układzie bilardowym.

---

## Funkcjonalności

* symulacja ruchu bil na stole bilardowym,
* zderzenia sprężyste pomiędzy bilami o jednakowych masach,
* odbicia od band stołu,
* uwzględnienie siły tarcia kinetycznego prowadzącej do zatrzymania układu,
* numeryczne całkowanie równań ruchu metodą półjawnego schematu Eulera,
* wizualizacja trajektorii ruchu bil,
* równoległe porównanie dwóch niemal identycznych układów dynamicznych,
* demonstracja efektu motyla poprzez analizę rozbieżności trajektorii.

---

## Model fizyczny

Przyjęto następujące założenia:

* ruch odbywa się w dwóch wymiarach,
* wszystkie bile mają jednakową masę i promień,
* pominięto ruch obrotowy bil,
* zderzenia kula--kula są doskonale sprężyste,
* odbicia od band traktowane są jako sprężyste zderzenia ze ścianami,
* uwzględniono tarcie kinetyczne,
* symulacja prowadzona jest w dyskretnych krokach czasowych.
---

## Efekt motyla

Program uruchamia równocześnie dwa niemal identyczne układy:

* **Układ A** -- ruch początkowy bez zaburzenia,
* **Układ B** -- ruch początkowy z niewielką zmianą kąta uderzenia.

Pomimo minimalnej różnicy parametrów początkowych, po serii zderzeń trajektorie bil mogą znacząco się różnić.

Stanowi to jakościową demonstrację **chaosu deterministycznego** i czułości układu na warunki początkowe.

---

## Struktura projektu

| Element          | Opis                                       |
| ---------------- | ------------------------------------------ |
| `Ball`           | reprezentuje pojedynczą bilę               |
| `BilliardSystem` | zarządza układem bil i obsługą fizyki      |
| `update()`       | aktualizacja ruchu w kroku czasowym        |
| `draw()`         | rysowanie obiektów i trajektorii           |
| `draw_panel()`   | panel informacyjny z parametrami symulacji |

---
### Wymagania

* Python 3.10 lub nowszy,
* biblioteka `pygame`.

## Sterowanie

| Klawisz  | Działanie                                  |
| -------- | ------------------------------------------ |
| `SPACJA` | restart symulacji                          |
| `P`      | pauza / wznowienie                         |
| `↑`      | zwiększenie różnicy kątów między układami  |
| `↓`      | zmniejszenie różnicy kątów między układami |
| `T`      | wyczyszczenie trajektorii                  |
| `ESC`    | zakończenie programu                       |

---
## Parametry symulacji

Domyślne wartości:

```python
G = 9.81
MU = 0.1
SCALE = 200
DT = 0.005
STOP_V = 1.5
```

gdzie:

* `G` -- przyspieszenie ziemskie [m/s²],
* `MU` -- współczynnik tarcia kinetycznego,
* `SCALE` -- przelicznik metrów na piksele,
* `DT` -- krok czasowy [s],
* `STOP_V` -- próg zatrzymania bili [px/s].

---

## Możliwe eksperymenty

Projekt umożliwia przeprowadzenie prostych eksperymentów numerycznych, takich jak:

* badanie wpływu współczynnika tarcia na czas wygaszania ruchu,
* obserwacja zmian trajektorii przy różnych kątach początkowych,
* analiza rozbieżności pomiędzy układami A i B,
* demonstracja odbić od band poprzez zmianę parametrów początkowych.

---

## Ograniczenia modelu

Model stanowi uproszczenie rzeczywistej gry w bilard i nie uwzględnia:

* ruchu obrotowego bil,
* poślizgu oraz toczenia,
* deformacji bil podczas zderzeń,
* wpływu łuz na przebieg rozgrywki,
* oporów powietrza.

---

## Autor

**Antoni Mosiołek**

Projekt wykonany w ramach zajęć z fizyki jako symulacja zachowań bil i ich wrażliwośći na warunki początkowe.
