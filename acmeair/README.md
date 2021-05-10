# Acme Air

A Tomcat-based revision of Acme Air sample microservices application. Our work is based upon [Joe McClure's Blueperf](https://github.com/blueperf) repo, which brings Spring framework to the original [Acme Air project](https://github.com/acmeair/acmeair) by Andrew Spyker initially. Since Joe's version uses Open Liberty as the Java application server, we rewrite Dockerfile to stick to the default setting within Spring Boot, that is Tomcat. Besides, we also remove both Auth Service from both the project and the code to fit the author's context. This repo is also the part of the author's MSc project for his graduation thesis. 

## Build & Run

To build the image, go to the subdir and execute docker build.

To run the project, we suggest deploying all the services onto a Kubernetes cluster (See 1_kubernetes). Remember to load data (flights, customers, ...). This can be done by call /load API (see belows).  

## APIs

The following lists some API calls examples, with 192.168.99.102 being the API gateway's address (more specifically, it's the address of Ingress) and `http` for HTTPie utility. It can be a reference since the upstream project doesn't detail these information.

### Get Prometheus Metrics

http 192.168.99.102/flight/prometheus

```
# HELP http_server_requests_seconds  
# TYPE http_server_requests_seconds summary
http_server_requests_seconds_count{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/health",} 25949.0
http_server_requests_seconds_sum{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/health",} 19.162667466
http_server_requests_seconds_count{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/loader/load",} 1.0
http_server_requests_seconds_sum{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/loader/load",} 1.691916666
http_server_requests_seconds_count{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/prometheus",} 8647.0
http_server_requests_seconds_sum{application="${spring.application.name}",exception="None",method="GET",outcome="SUCCESS",status="200",uri="/prometheus",} 27.232860394
http_server_requests_seconds_count{application="${spring.application.name}",exception="None",method="POST",outcome="SUCCESS",status="200",uri="/getrewardmiles",} 10711.0
http_server_requests_seconds_sum{application="${spring.application.name}",exception="None",method="POST",outcome="SUCCESS",status="200",uri="/getrewardmiles",} 12.555967168
```

### Get Service Health Status

http 192.168.99.102/flight/health

```
{
    "details": {
        "diskSpace": {
            "details": {
                "free": 10417446912,
                "threshold": 10485760,
                "total": 18211586048
            },
            "status": "UP"
        }
    },
    "status": "UP"
}
```

### Get Reward Miles

http -f POST 192.168.99.102/flight/getrewardmiles flightSegment='AA4'

```
{"miles": 230}
```

### Get Flight Info

http -f POST 192.168.99.102/flight/queryflights fromAirport='AMS' toAirport='LHR' fromDate='2021/04/25' returnDate='2021/04/25' oneWay='false'

```
{
    "tripFlights": [
        {
            "currentPage": 0,
            "flightsOptions": [
                {
                    "_id": "11365129-538f-4a26-a0da-e2c577eee127",
                    "airplaneTypeId": "B747",
                    "economyClassBaseCost": 200,
                    "firstClassBaseCost": 500,
                    "flightSegment": {
                        "_id": "AA4",
                        "destPort": "LHR",
                        "miles": 230,
                        "originPort": "AMS"
                    },
                    "flightSegmentId": "AA4",
                    "numEconomyClassSeats": 200,
                    "numFirstClassSeats": 10,
                    "scheduledArrivalTime": "Sun Apr 25 00:23:00 UTC 2021",
                    "scheduledDepartureTime": "Sun Apr 25 00:00:00 UTC 2021"
                }
            ],
            "hasMoreOptions": false,
            "numPages": 1,
            "pageSize": 10
        },
        {
            "currentPage": 0,
            "flightsOptions": [],
            "hasMoreOptions": false,
            "numPages": 1,
            "pageSize": 10
        }
    ],
    "tripLegs": 2
}
```

### Book a Flight

http -f POST 192.168.99.102/booking/bookflights userid='uid1@email.com' toFlightId='20a4e13e-764a-41d0-89c4-3f658fac9bbd' toFlightSegId='AA4' retFlightId='' retFlightSegId='' oneWayFlight='true'

```
{
    "departBookingId": "ffa5e391-27f4-420e-bc2f-fd5edb23aefa",
    "oneWay": true
}
```

### Load 10 Customers

192.168.99.102/customer/loader/load?numCustomers=10