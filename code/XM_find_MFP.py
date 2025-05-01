import numpy as np
import matplotlib.pyplot as plt
import sys
import signal
import XM_constants as XM

# Allow user to exit out of script early
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create debug plots when true
debug = True

# Create XM object
XM=XM.XM_sat()
XM.print_config()

# Load samples from file
filename = "XM_test_x2_sync.dat"
data_type = np.complex64
with open(filename, "rb") as file:
    data_array = np.fromfile(file, dtype=data_type)
samples = len(data_array)

# Display the amount of information in the frame
print("Data Duration (s) = ", samples/XM.fs)

FSP_in_file=int(samples/XM.samples_between_FSP)
MFP_in_file=int(samples/XM.samples_between_MFP)

print ("FSP in file = ", FSP_in_file)
print ("MFP in file = ", MFP_in_file)

# Find first FSP
# Data takes roughly 2s to lock (so ignore first 2s of data)
idx=int(2*XM.fs);
corr_out=np.correlate(data_array[idx:idx+XM.samples_between_FSP+XM.FSP_symbols], XM.FSP, 'full')
fsp_idx=idx+np.argmax(np.abs(corr_out))-XM.FSP_symbols+1
print ("first fsp found at ", fsp_idx, idx)
print ("FSP CHECK, should be the same")
print (1*(data_array[fsp_idx:fsp_idx+XM.FSP_symbols]>0))
print (1*(XM.FSP>0))

# Find MFP prior to FSP
idx = fsp_idx-XM.MFP_symbols
step = XM.MFP_symbols
mfp_step = XM.samples_per_frame 

# Loop for each possible MFP position
max_corr=0
max_index=0
for loop in range(FSP_in_file-8*XM.FSP_per_frame):

    # Auto-correlate with next MFP
    corr_out=np.correlate(data_array[idx+mfp_step:idx+step+mfp_step], data_array[idx:idx+step], 'full')

    # Keep track of the maximum correlation
    if np.max(np.abs(corr_out))>max_corr:
        max_corr=np.max(np.abs(corr_out))
        max_index=idx+np.argmax(np.abs(corr_out))-XM.MFP_symbols+1
        print (max_index, max_corr)
        if debug:
            plt.clf()
            plt.plot(np.abs(corr_out))
            plt.xlabel('Index')
            plt.ylabel('Magnitude')
            plt.title('MFP Auto-Correlation')
            plt.pause(0.5)
            
    # Move to next possible MFP position
    idx=idx+XM.samples_between_FSP

# Show best case results
plt.show()

# Output MFP
mfp_index=max_index
print ("last index = ", idx)
print ("mfp index = ", mfp_index)
print ("LIKELY MFP ")
print (1*(data_array[mfp_index:mfp_index+XM.MFP_symbols]>0))

# Plot constellation
preamble_symbols = data_array[mfp_index:mfp_index+step]
data_start = mfp_index + step + XM.FSP_symbols
data_end = data_start + XM.data_symbols
data_symbols = data_array[data_start:data_end]
plt.clf()
plt.scatter(np.real(data_symbols), np.imag(data_symbols))
plt.scatter(np.real(preamble_symbols), np.imag(preamble_symbols))
plt.xlabel('In-phase')
plt.ylabel('Quadrature')
plt.title('Constellation')
plt.legend(['Data Symbols', 'MFP Symbols'], loc='lower right')
plt.show()
print ("DONE")
