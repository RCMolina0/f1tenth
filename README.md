**TODO:** \
[x] control node \
[x] local planning \
[x] localization node

**Some details on what's going on:**
current repo - 
  perception - 
    listens to odom and publishes pose
    odom comes from [https://github.com/f1tenth/f1tenth_system](url) f1tenth_system repo
    gets rid of speed attribute
    
  local planner - 
    ignores perception, takes odometry and global race line (not implemented yet)
    finds point P on line closest to car
    publishes waypoint of destination with starting point being P
      does this via a radius and some linear algorithm
      
  control - 
    publishes speed and orientation to destination given waypoint

how repo is being run - 
  launch file (maybe works?) will run every node and f1tenth_system repo


slam_toolbox repo ([https://github.com/SteveMacenski/slam_toolbox](url)) - 
  used for localization and mapping
  runs localization at realtime
  mapping done previously using teleop (map 1 lap around)
  ran as a system package, but the node is separate
  launch file will maybe run slam_toolbox too


How to connect to car - 
  SSH via our IP address
    host f1tenth
    HostName 10.195.115.50
    User roboracer
    Password sig
  run our launch file
