!/usr/bin/bash

echo rusza ddd5.sh

x=10
echo "pliki kontrolne"
echo "$1"
echo "$2"
echo "$3"
echo "$4"
echo "$5"
echo "$6"
echo "$7"
echo "$8"
echo "$9"
echo "${10}"
echo liczba migrantow:  "${11}"
echo interwał migracji: "${12}"

for i in 0 1 2 3 4 5 6 7 8 9
do
  cd utils
  ./dd5.sh
  cd ..

  dda=$(date +%y%m%d)
  tta=$(date +g%H%M%S)
#  echo "$dda"
#  echo "$tta"

  python3 run_algorithm.py 0 "$dda" "$tta" 5 "${i}" "${11}" "${12}" &
  python3 run_algorithm.py 1 "$dda" "$tta" 5 "${i}" "${11}" "${12}" &
  python3 run_algorithm.py 2 "$dda" "$tta" 5 "${i}" "${11}" "${12}" &
  python3 run_algorithm.py 3 "$dda" "$tta" 5 "${i}" "${11}" "${12}" &
  python3 run_algorithm.py 4 "$dda" "$tta" 5 "${i}" "${11}" "${12}" &
# param: 1. num wyspy 2. data 3. czas 4. ile wysp 5. seria 6. il_emigr 7. interwał

  if [ "${i}" == 0 ]
  then
    a=1
    until [ -e "$1" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 1 ]
  then
    a=1
    until [ -e "$2" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 2 ]
  then
    a=1
    until [ -e "$3" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 3 ]
  then
    a=1
    until [ -e "$4" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 4 ]
  then
    a=1
    until [ -e "$5" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 5 ]
  then
    a=1
    until [ -e "$6" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 6 ]
  then
    a=1
    until [ -e "$7" ]
    do
      b=a;
    done
  fi

  if [ "${i}" == 7 ]
  then
    a=1
    until [ -e "$8" ]
    do
      b=a;
    done
  fi

    if [ "${i}" == 8 ]
  then
    a=1
    until [ -e "$9" ]
    do
      b=a;
    done
  fi

      if [ "${i}" == 9 ]
  then
    a=1
    until [ -e "${10}" ]
    do
      b=a;
    done
  fi

done

echo "ddd5w10s done"
