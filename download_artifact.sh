#!/bin/sh
output=$(docker cp fuzzer:/usr/src/report/junit_fuzzing_report.xml junit_fuzzing_report.xml 2>&1)
output=$(echo $output|wc -w )
while [ "$output" -gt 1 ]; do
  output=$(docker cp fuzzer:/usr/src/report/junit_fuzzing_report.xml junit_fuzzing_report.xml 2>&1);
  output=$(echo $output|wc -w );
done