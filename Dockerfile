FROM alpine:edge

ADD ./ /tmp/install/

RUN apk update && \
    apk add python3 python3-dev musl-dev curl curl-dev gcc && \
    cd /tmp/install && \
    curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    pip3 install -e .

EXPOSE 80

CMD aufseher
