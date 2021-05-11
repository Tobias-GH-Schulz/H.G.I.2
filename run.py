import os
from multiprocessing import Pool, freeze_support                                                
                                                                                
                                                                                
processes = ('memcached', 'python hand_gesture.py', 'python control_dash_app.py')                                    
                                                  
                                                                                
def run_process(process):                                                             
    os.system(process)                                       

 

if __name__ == '__main__':
    freeze_support()                                                        
    pool = Pool(processes=3)                                                        
    pool.map(run_process, processes)        