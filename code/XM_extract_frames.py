import numpy as np
import matplotlib.pyplot as plt
import sys
import signal
import XM_constants as XM
import os

# Remove old data file
if os.path.exists('mfp_data.npy'):
    os.remove('mfp_data.npy')

# Create a new data file
mfp_file = open('mfp_data.npy', 'ab')

# Allow user to exit out of script early
def signal_handler(sig, frame):
    global mfp_file
    print('You pressed Ctrl+C!')
    mfp_file.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create XM Object
XM=XM.XM_sat()

# Specs for input file
filename = "XM_test_x2_sync.dat"
data_type = np.complex64

# Flags to specify whether data is synchronized
FSP_SYNC=False
MFP_SYNC=False

# Jump into file as AGC may not be stable
idx=int(.0*XM.fs)
samples = XM.samples_between_FSP

# Array of data symbols in frame (+ padding for last group of symbols)
MFP_symbols=np.zeros((XM.FSP_per_frame*XM.data_symbols), dtype=data_type)

# Array of bits
MFP_bits=np.zeros(2*XM.data_symbols_per_frame, dtype=float)

with open(filename, "rb") as file:

    # Loop until all the samples have been read from the file
    while(1):

        # Grab data between FSP symbols
        data_array = np.fromfile(file, dtype=data_type,  count=1*samples)

        # Synchronize to FSP
        if not FSP_SYNC:

            # Find the peak correlation index
            corr_out=np.correlate(data_array,XM.FSP)
            max_index=np.argmax(np.abs(corr_out))
            
            # Use the average energy to set a threshold
            ave=np.sum(np.abs(corr_out))/len(corr_out)

            # If peak exceeds threshold by enough, declare that the FSP is found
            if ((np.abs(corr_out[max_index])/ave)>4):

                # No longer look for FSP
                FSP_SYNC=True
                
                # Print some stats when FSP is found
                print(int(idx/8)+max_index, max_index, np.abs(corr_out[max_index])/ave)
                
                # Navigate to start of FSP
                # Multiply by 8 for bytes in np.complex64
                idx=idx+max_index*8
                file.seek(idx)

                print("FOUND FSP", idx)

            # Next FSP should show up at a predictable position
            else:
                idx+=samples*8

        # Synchronize to MFP
        elif not MFP_SYNC:

            # Find the peak correlation index
            corr_out=np.correlate(data_array,XM.MFP)
            max_index=np.argmax(np.abs(corr_out))

            # Use the average energy to set a threshold
            ave=np.sum(np.abs(corr_out))/len(corr_out)

            # Move to next possible FSP position
            idx+=samples*8
            
            # Check for data that exceeds threshold
            # Ignore first frame
            if ((np.abs(corr_out[max_index])/ave)>4 and max_index>=samples-XM.MFP_symbols):
                
                # Mark MFP as found and reset indices
                print("FOUND MFP", idx)
                MFP_SYNC=True
                FSP_index=0
                MFP_frame_index=0
                MFP_SYMBOLS=[]

        # Data is syncrhnoized
        else:

            # Move to start of next FSP
            idx+=samples*8

            # Look for when frame is complete
            if (FSP_index==(XM.FSP_per_frame)):

                # Print some helpful messages
                print(MFP_frame_index, "MFP FRAME COMPLETE", idx)
                print (len(MFP_SYMBOLS))

                # Update indices
                MFP_frame_index+=1
                FSP_index=0

                # Save the real and imaginary parts of the data
                MFP_bits[0:len(MFP_bits):2]=np.real(MFP_SYMBOLS[:-XM.MFP_symbols-XM.pad_symbols])
                MFP_bits[1:len(MFP_bits):2]=np.imag(MFP_SYMBOLS[:-XM.MFP_symbols-XM.pad_symbols])

                # Save frame to file
                np.save(mfp_file,MFP_bits)

            # Save subregion of frame
            else:
                MFP_SYMBOLS[FSP_index*XM.data_symbols:(FSP_index+1)*XM.data_symbols] = (data_array[XM.FSP_symbols:])
                FSP_index+=1

        if (len(data_array)==0): break

# Close numpy file
mfp_file.close()

# Save data to .mat file
if True:

    # Load numpy data
    data = np.load('mfp_data.npy')

    # Save to .mat file
    import scipy.io as sio
    sio.savemat('mfp_data.mat',{'data': data})
