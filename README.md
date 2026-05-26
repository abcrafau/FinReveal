# FinReveal

FinReveal to aplikacja webowa w Streamlit do automatycznej analizy sprawozdań finansowych. Umożliwia wczytanie plików Excel, XML albo XAdES, rozpoznaje kluczowe pozycje finansowe, liczy wskaźniki i prezentuje wyniki w formie tabel oraz wykresów trendów.

## Demo

Publiczna wersja aplikacji jest dostępna tutaj:

[https://finreveal.streamlit.app/](https://finreveal.streamlit.app/)

## Najważniejsze funkcje

- obsługa sprawozdań finansowych w formatach `xlsx`, `xml` i `xades`,
- możliwość wgrania jednego albo kilku plików tej samej spółki,
- łączenie okresów z kilku sprawozdań w jedną analizę,
- zabezpieczenie przed zdublowaniem dwóch plików dotyczących tego samego roku sprawozdania,
- wybór roku analizy po wczytaniu danych,
- szybkie podsumowanie najważniejszych wartości: przychodów, zysku netto, aktywów razem i kapitału własnego,
- obliczanie wskaźników rentowności, płynności, zadłużenia i sprawności działania,
- prezentacja wzorów użytych do obliczenia wskaźników,
- wykresy trendów dla pozycji finansowych i wskaźników,
- podgląd danych rozpoznanych przez aplikację.

## Obsługiwane dane

Dla plików Excel aplikacja oczekuje arkuszy:

- `Bilans`
- `RZiS`
- `RPP`

Dla plików XML/XAdES aplikacja odczytuje dane ze struktury sprawozdania finansowego i pobiera wartości dla bieżącego oraz poprzedniego okresu.

## Uruchomienie lokalne

Zainstaluj zależności:

```powershell
pip install -r requirements.txt
```

Uruchom aplikację:

```powershell
streamlit run app.py
```

W tym projekcie możesz też użyć pliku:

```powershell
.\start_app.bat
```

Domyślny lokalny adres aplikacji:

```text
http://127.0.0.1:8510
```

## Technologie

- Python
- Streamlit
- pandas
- Plotly
- openpyxl
- Pillow

## Autor

Rafał Kopliński

- LinkedIn: [linkedin.com/in/rafal-koplinski](https://www.linkedin.com/in/rafal-koplinski/)
- GitHub: [github.com/abcrafau](https://github.com/abcrafau)
