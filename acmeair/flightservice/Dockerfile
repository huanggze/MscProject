FROM maven:3.8.1-openjdk-11 as builder
COPY . /
RUN mvn clean package

FROM openjdk:11.0.10-jre-slim
WORKDIR /app/
COPY --from=builder /target/acmeair-flightservice-springboot-2.1.1-SNAPSHOT.jar /app/

CMD java -jar /app/acmeair-flightservice-springboot-2.1.1-SNAPSHOT.jar