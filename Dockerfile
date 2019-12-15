FROM python:alpine as base

FROM base as builder
WORKDIR /src
ADD . .
RUN python setup.py bdist_wheel

FROM base
COPY --from=builder /src/dist /dist
RUN apk add --no-cache -t build gcc musl-dev \
 && pip install --no-cache-dir /dist/*whl \
 && apk del build \
 && rm -r /dist
EXPOSE 80
CMD aufseher
