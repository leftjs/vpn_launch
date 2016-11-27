PID=`ps -ef | grep launch.py | grep -v grep | awk '{print $2}'`
if [[ "" != "$PID" ]];
then
  echo "killing $PID"
  kill -9 $PID
fi
