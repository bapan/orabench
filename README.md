# orabench
A Simple Benchmark Tools for Oracle V1.0. 
This program simulate concurrency insert to a order table.

orabench.cfg is a config,like below :

[config]
db=test/test@192.168.56.13:1521/orcl    -- Connection Str for Oracle
concurrency=100                         -- Number of Process started 
requests=1000                           -- Number of Insert requested per process
think_time=0.01                         -- Think Time Per Insert
init=y                                  -- If is 'y' , create orders table , if not don't create    

