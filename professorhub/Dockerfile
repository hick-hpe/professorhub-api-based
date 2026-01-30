# Informa a imagem base
FROM python:3
# Define o ambiente
ENV PYTHONUNBUFFERED=1
# Esta será o diretorio onde nosso projeto irá rodar
WORKDIR /code
# Copia o arquivo de dependências do projeto para o diretório
COPY requirements.txt /code/
RUN pip install --no-cache-dir psycopg2-binary
# Instala as dependências do arquivo
RUN pip install -r requirements.txt
# Copia os arquivos da raiz para o diretório
COPY . /code/
ENTRYPOINT ["sh", "-c"]
CMD ["python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
