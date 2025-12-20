# K1 (PI1)

Ovo je jednostavan kontrolni program za PI1 (prva kontrolna tačka)

Sadržaj:
- `pi1.py` — glavni fajl. Pokreće čitače senzora i pruža interaktivni konzolni interfejs za upravljanje aktuatorima.
- `devices.py` — definicije uređaja (senzori i aktuatori). Ima jednostavne simulirane implementacije.

Karakteristike:
- Moguće je pokrenuti u režimu simulacije (`--simulate-all`)
- Senzori se periodično čitaju i njihove vrednosti se ispisuju u konzolu
- Aktuatori (LED i Buzzer) mogu se kontrolisati preko konzole komandama

Primeri pokretanja:
```
python pi1.py --simulate-all
python pi1.py --simulate-all --run-duration 10
```

Komande u interaktivnom režimu:
- `led on` / `led off` — uključi/isključi `DL` (Door Light)
- `buzzer on` / `buzzer off` — uključi/isključi `DB` (Door Buzzer)
- `status` — prikaži stanje aktuatora
- `help` — prikaži pomoć
- `exit` — izlaz
