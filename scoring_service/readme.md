# Mikroserwis do modeli rekomendacyjnych.

## Instalacja i uruchomienie

Serwis może zostać uruchomiony na dwa sposoby: "ręcznie" poprzez utworzenie wirtualnego środowiska python i instalację
odpowiednich zależności lub za pośrednictwem `Docker` na podstawie dostarczonego wraz z projektem `Dockerfile`.

### Uruchomienie "ręczne" bez Docker'a

1. Utworzyć nowe wirtualne środowisko python: `python -m venv .venv`
2. Przejść do folderu z mikroserwisem: `cd microservice`
3. Zainstalować zależności: `pip3 install -r requirements.txt`
4. Przejść do folderu src: `cd src`
5. Uruchomić mikroserwis (tutaj na porcie 5555): `uvicorn --host 127.0.0.1 --port 5555 recommendation_service.app:app`

### Uruchomienie za pośrednictwem Docker

1. Przejść do folderu z mikroserwisem: `cd microservice`
2. Zbudować obraz Docker'a: `docker build -t recomendation_system:1 .`
3. Uruchomić zbudowany obraz Docker'a i przekierować porty (tutaj na port
   5555): `docker run -p 5555:80 recomendation_system:1`