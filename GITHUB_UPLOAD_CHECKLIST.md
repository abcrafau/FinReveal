# GitHub upload checklist

## Przed publikacja

- Sprawdz, czy w projekcie nie ma prawdziwych sprawozdan finansowych ani danych klientow.
- Nie dodawaj plikow `.env`, kluczy API, hasel ani plikow certyfikatow.
- Nie publikuj folderu `.venv`, cache, logow ani lokalnych eksportow.
- Jezeli chcesz pokazac przykladowy plik Excel, uzyj tylko danych testowych/anonymizowanych.

## Co powinno trafic do repozytorium

- `app.py`
- `src/`
- `assets/app_icon.png`
- `README.md`
- `requirements.txt`
- `start_app.bat`
- `.gitignore`
- `.gitattributes`
- `GITHUB_UPLOAD_CHECKLIST.md`

## Komendy po zainstalowaniu Git

```powershell
git init
git add .
git status
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TWOJ_LOGIN/NAZWA_REPO.git
git push -u origin main
```

Przed `git commit` sprawdz wynik `git status`. Nie powinno tam byc `.venv`, `__pycache__`, plikow `.log`, prywatnych Exceli ani plikow `.env`.
