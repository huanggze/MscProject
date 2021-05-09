# Experiments

## 1. Auto-scaling Performance Test for a single Service

The scaling target we examine is Flight Service. We use JMeter to generate and feed loads. 

First, let Flight Service flies with constant, moderate traffic demand for over 5 minutes. Then start adding loading. Record the time spent for this auto-scaling test. Flight Service is expected to bring replicas from 1 to 3.

```
jmeter -n -t test_plan_1.jmx -l log_1.jtl 
```

## 2. Auto-scaling Performance Test for coordinated Services

## 3. Image Size

## 4. Container Runtime