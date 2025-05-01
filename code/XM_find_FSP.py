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

# Data takes roughly 2s to lock (so ignore first 2s of data)
idx=int(2*XM.fs)
step=XM.FSP_symbols
fsp_step=XM.samples_between_FSP

# Loop for each possible FSP position
max_corr=0
max_idx=0
for loop in range(10*XM.samples_between_FSP):

    # Auto-correlate with next FSP
    corr_out=np.correlate(data_array[idx:idx+step], data_array[idx+fsp_step:idx+fsp_step+step], 'full')

    # Keep track of the maximum correlation
    if np.max(np.abs(corr_out))>max_corr:
        print (idx, np.max(np.abs(corr_out)))
        max_corr=np.max(np.abs(corr_out))
        max_idx=idx
        # Plot results
        # plt.clf()
        # plt.plot(np.abs(corr_out))
        # plt.xlabel('Index')
        # plt.ylabel('Magnitude')
        # plt.title('FSP Auto-Correlation')        
        # plt.pause(0.5)
    idx+=1

# Show best results
# plt.show()

# Print results
print ("last test = ",idx)
print ("best idx = ", max_idx)

# Add 10 to increase SNR
fsp_mrc=np.zeros(step, dtype=np.complex64)
for loop in range(10):
    fsp_mrc=fsp_mrc+data_array[max_idx:max_idx+step]
    max_idx=max_idx+fsp_step

# Output FSP
print ("FPS Sequence = ", 1*(fsp_mrc>0))

# Plot constellation
preamble_symbols = data_array[max_idx:max_idx+step]
data_symbols = data_array[max_idx+step:max_idx+fsp_step]
plt.clf()
plt.scatter(np.real(data_symbols), np.imag(data_symbols))
plt.scatter(np.real(preamble_symbols), np.imag(preamble_symbols))
plt.xlabel('In-phase')
plt.ylabel('Quadrature')
plt.title('Constellation')
plt.legend(['Data Symbols', 'FSP Symbols'], loc='lower right')
plt.show()
print ("DONE")