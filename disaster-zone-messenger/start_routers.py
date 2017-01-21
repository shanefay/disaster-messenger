import router
import listenThread

# TODO:
#   Ensure ALL folders exist before trying to access them

# script for setup functions
import utility    
# For the loop
import time

#router1 = router.DisasterRouter(8888)
#router2 = router.DisasterRouter(8889)
#router3 = router.DisasterRouter(8890)
#router4 = router.DisasterRouter(8892)
#router5 = router.DisasterRouter(8893)
#router6 = router.DisasterRouter(8894)

router1 = router.DisasterRouter(8888)
router2 = router.DisasterRouter(8890)
router3 = router.DisasterRouter(8892)
router4 = router.DisasterRouter(8894)
router5 = router.DisasterRouter(8895)
router6 = router.DisasterRouter(8896)
router7 = router.DisasterRouter(8898)
router8 = router.DisasterRouter(8900)

# Listening threads for each router
listenThread.ListenThread(router1)
listenThread.ListenThread(router2)
listenThread.ListenThread(router3)
listenThread.ListenThread(router4)
listenThread.ListenThread(router5)
listenThread.ListenThread(router6)
listenThread.ListenThread(router7)
listenThread.ListenThread(router8)

router1.discovery()
router2.discovery()
router3.discovery()
router4.discovery()
router5.discovery()
router6.discovery()
router7.discovery()
router8.discovery()

#Ensure discovery ends before creating network map
time.sleep(2)

routers = [router1, router2, router3, router4, router5, router6, router7, router8]
utility.create_network_map(routers)

utility.create_dvr_routing_tables()

# Keeps the script running in a somewhat efficient manner
while True:
    time.sleep(1)