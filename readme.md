# Readme

## Requisitos
Python e virtualenv

extrair arquivo base_de_dados

#### Python
Instalar Python 3.8.3

### docker compose
docker-compose up

#### Virtualenv
caso não tenha virtualenv instalado no diretorio do python
abrir diretorio onde esta instalado python
```bash
cd C:\Python38\Scripts
pip install virtulenv
```
criar virtualenv no diretório raiz do atual projeto para armazenamento de libs caso ainda não exista
```bash
cd <DIRETORIO DO PROJETO>
C:\Python38\Scripts\virtulenv.exec venv
```

## Start

```bash
pip install -r requirements-dev.txt
python .\main.py run --host=0.0.0.0 --port=8000
```


## Documentacao dispível em
[link](http://ecm.api.simpleagro.com.br:8000/doc/ "http://ecm.api.simpleagro.com.br:8000/doc/").


## habilitar lint python
python.linting.pylintEnabled
