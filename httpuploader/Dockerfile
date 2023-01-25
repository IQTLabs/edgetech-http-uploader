FROM iqtlabs/edgetech-core:latest
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
ADD ./http_uploader_pub_sub.py .
ENTRYPOINT [ "python3", "-u", "http_uploader_pub_sub.py" ]