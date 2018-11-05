FROM python:alpine as builder
WORKDIR /repo
ADD . .
RUN python setup.py bdist_wheel

FROM python:alpine
COPY --from=builder /repo/dist /dist
RUN apk add --no-cache curl && \
    apk add --no-cache -t .dev curl-dev gcc musl-dev && \
    pip install --no-cache-dir /dist/*whl && \
    apk del .dev
EXPOSE 80
CMD aufseher
