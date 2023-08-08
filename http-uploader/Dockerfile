FROM iqtlabs/edgetech-core:latest
RUN pip3 install poetry==1.5.1

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY ./http_uploader_pub_sub.py .
ENTRYPOINT [ "python3", "http_uploader_pub_sub.py" ]
