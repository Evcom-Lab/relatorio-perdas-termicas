FROM python:3.10

WORKDIR /usr/app

ARG STREAMLIT_PATH="/root/.streamlit/"

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt



RUN mkdir -p $STREAMLIT_PATHCOPY .streamlit/config.toml $STREAMLIT_PATH
COPY .streamlit/config.toml $STREAMLIT_PATH 

EXPOSE 8517

COPY . .

CMD streamlit run --server.port 8517 --server.enableCORS false relatorio.py

