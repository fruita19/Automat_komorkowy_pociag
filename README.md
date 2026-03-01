🚄 O projekcie
Aplikacja stanowi implementację modelu automatów komórkowych do symulacji i wizualizacji ruchu pociągów na wielopoziomowej infrastrukturze torowej. Projekt został opracowany jako zaliczenie akademickie, koncentrując się na logice sterowania ruchem i rozwiązywaniu konfliktów w czasie rzeczywistym.

🛠️ Architektura i Logika
Symulacja opiera się na dyskretnych krokach czasowych (tzw. ticks), w których każdy pociąg podejmuje decyzje na podstawie stanu otaczających go komórek:
1.Struktura sieci: Trzy główne pierścienie (Black, Orange, Green) połączone inteligentnymi zwrotnicami (Transfer Switches).
2.Zarządzanie kolizjami: System rezerwacji toru analizuje zamierzenia (intents) wszystkich jednostek. W przypadku sporu o tę samą komórkę, priorytet otrzymuje pociąg o dłuższym czasie oczekiwania.
3.Dynamika stacji: Pociągi automatycznie wykrywają wolne perony, zjeżdżają na bocznicę i realizują postój o zdefiniowanej długości (Dwell Time).
4.Sygnalizacja: Dynamiczna aktualizacja sygnałów świetlnych w oparciu o zajętość kolejnych sekcji toru.

🎮 Interfejs użytkownika
1.W dolnej części ekranu znajdują się przyciski sterujące:
2.Start/Pause: Kontrola upływu czasu symulacji.
3.Step: Ręczne wymuszenie jednego kroku (ticka).
4.Reset: Powrót do konfiguracji początkowej świata.
