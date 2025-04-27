import numpy as np
import matplotlib.pyplot as plt
import sys
import signal
sys.path.append("/media/sf_VM_shared/ECE531/Final/python_tools")
import XM_constants as XM
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


filename = "XM_test_x2_sync.dat"
data_type = np.complex64  # Replace with the correct data type
XM=XM.XM_sat()
print("samples between MFP = ", int(XM.frame_time*XM.fs))
print("samples per MFP = ", (XM.MFP_symbols*XM.fs/XM.symbol_rate))
print("samples per FSP = ", (XM.FSP_symbols*XM.fs/XM.symbol_rate))
print("samples between FSP = ", XM.Data_symbols*XM.fs/XM.symbol_rate)
print("samples per frame = ",XM.samples_per_frame*XM.fs/XM.symbol_rate )
samples_between_frames=XM.samples_per_frame*XM.fs/XM.symbol_rate
samples_between_FSP=int(XM.FSP_symbols+XM.Data_symbols*XM.fs/XM.symbol_rate)
print("samples per second = ",XM.samples_per_frame*XM.fs/(XM.symbol_rate*XM.frame_time) )

with open(filename, "rb") as file:
    data_array = np.fromfile(file, dtype=data_type)
samples=len(data_array)
print(samples/XM.fs)
# about 2 seconds in, then locked
idx=int(2*XM.fs);
step=XM.FSP_symbols
fsp_step=samples_between_FSP;
max_corr=0
max_idx=0
FSP_in_file=int(samples/samples_between_FSP)
for loop in range(10*samples_between_FSP):
    corr_out=np.correlate(data_array[idx:idx+step], XM.FSP,'full')
    if np.max(np.abs(corr_out))>max_corr:
        #print (idx, np.max(np.abs(corr_out)))
        max_corr=np.max(np.abs(corr_out))
        max_idx=idx
    idx+=1
print ("last test = ",idx)
print ("best idx = ", max_idx)
#add 10
fsp_mrc=np.zeros(step, dtype=np.complex64)
for loop in range(10):
    fsp_mrc=fsp_mrc+data_array[max_idx:max_idx+step]
    max_idx=max_idx+fsp_step
print ("FPS Sequence = ", 1*(fsp_mrc>0))
print ("DONE")
