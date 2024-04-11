!/bin/bash

# parametry:
# 1. data np. 221006
# 2. problem na 4 znakach od dużej litery, np. Sphe, Rast
# 3. wymiar problemu, np. 10, 50, 100

echo "date problem dim: " "$1" "$2" "$3"

for j in 5 15 25   #5 15 25 35 # migration interval
do

  for i in 5 10  # 5 10 15 20 number of migrants
  do

    echo "number of migrants: " "$i" "interval:" "$j"

    ./ddd5w10s.sh logs/"$1"/"$2""$3"/seriaEnd0.txt logs/"$1"/"$2""$3"/seriaEnd1.txt logs/"$1"/"$2""$3"/seriaEnd2.txt logs/"$1"/"$2""$3"/seriaEnd3.txt logs/"$1"/"$2""$3"/seriaEnd4.txt logs/"$1"/"$2""$3"/seriaEnd5.txt logs/"$1"/"$2""$3"/seriaEnd6.txt logs/"$1"/"$2""$3"/seriaEnd7.txt logs/"$1"/"$2""$3"/seriaEnd8.txt logs/"$1"/"$2""$3"/seriaEnd9.txt "$i" "$j"

    kat="logs/""$1""/"$2""$3"/seriaEnd9.txt"

    echo kat
    echo $kat

    a=1
    until [ -e "${kat}" ]
    do
      b=a;
    done

    python3 delSeria10Files.py "$1" "$2" "$3"

    echo "del uruch5w10s"
  done
done
