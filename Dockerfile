FROM python:alpine as builder
ADD . .
RUN python setup.py bdist_wheel

FROM python:alpine
COPY --from=builder /dist /dist
RUN apk add curl && \
    apk add -t .dev curl-dev gcc musl-dev && \
    pip install /dist/*whl && \
    apk del .dev && \
    rm -rf /var/cache/apk/* ~/.cache
EXPOSE 80
CMD aufseher
