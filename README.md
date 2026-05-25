# FinReveal

Prosta aplikacja do automatycznej analizy sprawozdań finansowych. Pierwsza wersja obsługuje pliki Excel z arkuszami:

- `Bilans`
- `RZiS`
- `RPP`

Aplikacja wczytuje pozycje sprawozdania, liczy podstawowe wskaźniki finansowe i generuje krótki komentarz analityczny.

## Uruchomienie

```powershell
pip install -r requirements.txt
streamlit run app.py
```

W tym projekcie możesz też uruchomić aplikację przez plik:

```powershell
.\start_app.bat
```

Adres aplikacji:

```text
http://127.0.0.1:8510
```

## Zakres wersji MVP

- wczytanie sprawozdania finansowego z Excela albo XML/XAdES,
- możliwość wgrania kilku plików XML/XAdES tej samej spółki i połączenia okresów w jedną analizę,
- scalanie kolejnych sprawozdań z nakładającym się okresem; dla powielonego roku aplikacja wybiera dane z raportu o wyższym roku,
- blokada wczytywania dwóch plików dotyczących tego samego roku sprawozdania, aby nie zdublować danych,
- ekstrakcja najważniejszych pozycji bilansu, rachunku zysków i strat oraz rachunku przepływów pieniężnych,
- obliczenie pełnego zestawu wskaźników z projektu: rentowności, płynności, zadłużenia i sprawności działania,
- obsługa plików z wieloma okresami oraz wybór roku analizy przez użytkownika,
- wygenerowanie prostego komentarza analitycznego,
- prezentacja trendów pozycji finansowych i wskaźników na wykresach z możliwością wyboru zakresu.
