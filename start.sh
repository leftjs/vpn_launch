PID=`ps -ef | grep launch.py | grep -v grep | awk '{print $2}'`
if [[ "" == "$PID" ]];
then
  echo "starting launch.py"
  python /home/pi/vpn_launch/launch.py &
fi
