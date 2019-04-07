FROM python:alpine as base

FROM base as builder
WORKDIR /src
ADD . .
RUN python setup.py bdist_wheel

FROM base
COPY --from=builder /src/dist /dist
RUN pip install --no-cache-dir /dist/*whl \
 && rm -r /dist
EXPOSE 80
CMD aufseher
