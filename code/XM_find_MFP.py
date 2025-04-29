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
samples_between_frames=int(XM.samples_per_frame*XM.fs/XM.symbol_rate)
samples_between_FSP=int(XM.FSP_symbols+XM.Data_symbols*XM.fs/XM.symbol_rate)
print("samples per second = ",XM.samples_per_frame*XM.fs/(XM.symbol_rate*XM.frame_time) )

with open(filename, "rb") as file:
    data_array = np.fromfile(file, dtype=data_type)
samples=len(data_array)
print(samples/XM.fs)
# about 2 seconds in, then locked
idx=int(2*XM.fs);
FSP_in_file=int(samples/samples_between_FSP)
MFP_in_file=int(samples/samples_between_frames)

print ("FSP in file = ", FSP_in_file)
print ("MFP in file = ", MFP_in_file)

# find first FSP
corr_out=np.correlate(data_array[idx:idx+samples_between_FSP+XM.FSP_symbols],XM.FSP,  'full')
fsp_idx=idx+np.argmax(np.abs(corr_out))-XM.FSP_symbols+1
print ("first fsp found at ", fsp_idx, idx)
print ("FSP CHECK, should be the same")
print (1*(data_array[fsp_idx:fsp_idx+XM.FSP_symbols]>0))
print (1*(XM.FSP>0))

idx=fsp_idx-XM.MFP_symbols #MFP prior to FSP
step = XM.MFP_symbols
mfp_step = XM.samples_per_frame 
print (mfp_step )
max_corr=0
max_index=0
for loop in range(FSP_in_file-8*XM.FSP_per_frame):
    corr_out=np.correlate( data_array[idx+mfp_step:idx+step+mfp_step],data_array[idx:idx+step],'full')
    if np.max(np.abs(corr_out))>max_corr:
        max_corr=np.max(np.abs(corr_out))
        max_index=idx+np.argmax(np.abs(corr_out))-XM.MFP_symbols+1
        plt.clf()
        plt.plot(np.abs(corr_out))
        plt.xlabel('Index')
        plt.ylabel('Magnitude')
        plt.title('MFP Correlation')
        plt.pause(0.1)
        print (max_index, max_corr)
    idx=idx+samples_between_FSP
plt.show()
mfp_index=max_index
print ("last index = ", idx)
print ("mfp index = ", mfp_index)
print ("LIKELY MFP ")
print (1*(data_array[mfp_index:mfp_index+XM.MFP_symbols]>0))
