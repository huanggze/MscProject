FROM golang:1.16.3-alpine3.13 AS builder

WORKDIR /build
COPY . .
RUN go build -o main .

FROM golang:1.16.3-alpine3.13

WORKDIR /app
COPY --from=builder /build/main /app/

ENTRYPOINT ["/app/main"]