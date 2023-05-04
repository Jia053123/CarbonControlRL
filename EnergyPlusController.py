from pyenergyplus.api import EnergyPlusAPI
from QueueOfOne import QueueOfOne
import threading

class EnergyPlusRuntimeController:
    def __init__(self): 
        self.energyplus_api = EnergyPlusAPI()
        self.dataExchange = self.energyplus_api.exchange

        self.energyplus_exec_thread: threading.Thread = None
        self.energyplus_state = None
        self.runtime = None
        self.exitCode = None
        return
    
    def createRuntime(self):
        rt = self.energyplus_api.runtime
        return rt

    def start(self, runtime, idfPath, epwPath, outputDir):
        self.runtime = runtime
        self.energyplus_state = self.energyplus_api.state_manager.new_state()

        def _run_energyplus(runtime, state, exitCode):
            print("starting up EnergyPlus simulaiton")
            exitCode = runtime.run_energyplus(state, ['-d', outputDir, '-w', epwPath, idfPath])
            return
        
        self.energyplus_exec_thread = threading.Thread(
            target=_run_energyplus,
            args=(self.runtime, self.energyplus_state, self.exitCode)
        )
        self.energyplus_exec_thread.start()
        return

    def stop(self): 
        print("stopping energy plus +++++++++++++++++++++++++++++++++++++++++")
        self.energyplus_api.runtime.clear_callbacks()
        self.energyplus_api.state_manager.reset_state(self.energyplus_state)
        self.energyplus_api.state_manager.delete_state(self.energyplus_state) 
        
        if self.energyplus_exec_thread is not None:
            self.energyplus_exec_thread.join()
            self.energyplus_exec_thread = None
            print("energy plus stopped +++++++++++++++++++++++++++++++++++++++++")
  
        return