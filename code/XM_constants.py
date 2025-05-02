import matplotlib.pyplot as plt
import numpy as np

class XM_sat:
    def __init__(self, fs=1.64e6):

        # Save input parameters
        self.fs=fs

        # Parameters from US8260192
        self.symbol_rate    = 1.64e6
        self.frame_time     = 0.432
        self.MFP_symbols    = 64
        self.FSP_symbols    = 32
        self.data_symbols   = 3424
        self.pad_symbols    = 96
        self.FSP_per_frame  = 205
        
        # Preambles computed from the data. Ambiguous by 180 degrees.
        # Assuming first BPSK symbol is a 1.
        FSP = -np.array([-1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,
                        1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1])
        self.FSP=FSP*(1+1j)
        MFP = np.array([-1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, -1, 1, -1, -1,
                         1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1,
                         1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1, 1, -1,
                         -1, -1, 1, -1, 1, 1])
        self.MFP=MFP*(1+1j)

    def get_freq_est(self, data, debug=False):

        # Determine the span of the FFT
        span=int(self.samples_between_FSP)
        
        # Locate the FSP
        corr_out=np.correlate(data, self.FSP)
        max_FSP=np.argmax(np.abs(corr_out))
        print("FSP found at ", max_FSP)

        # Raise data to the 4th power to remove QPSK modulation
        freq_fft=np.abs(np.fft.fft(data**4))
        max_freq_bin=np.argmax(freq_fft)
        print("freq bin = ", max_freq_bin)

        # Scale frequency by 1/4 to remove effects of raising data to the 4th power
        freq_per_bin = self.fs/(4*span)

        # Estimate fractional bin offset
        bin_offset=self.interp(freq_fft[max_freq_bin-1], freq_fft[max_freq_bin], freq_fft[max_freq_bin+1])

        # Determine frequency offset in Hz
        course_freq_est=(max_freq_bin+bin_offset)*freq_per_bin
        print ("Course freq estimate = ", course_freq_est)

        # Plot the angle of the data after removing the frequency offset
        # Should not drift across time
        if (debug):
            t=np.arange(span)/self.fs
            temp_data=data*np.exp(-1j*2*np.pi*course_freq_est*t)
            plt.plot(np.angle(temp_data),'b.')
            plt.show()
        return course_freq_est
    
    def interp(self, ym1,y0,yp1):
        p = (yp1 - ym1)/(2*(2*y0 - yp1 - ym1)); #position
        y = y0 - 0.25*(ym1-yp1)*p; #height
        return p

    # Define dependent read-only properties with getter function
    @property
    def symbols_per_frame(self):
        # Last frame includes implict padding and MFP
        return int(self.FSP_per_frame*(self.FSP_symbols+self.data_symbols))
    
    @property
    def data_symbols_last(self):
        return int(self.data_symbols - self.MFP_symbols - self.pad_symbols)
    
    @property
    def data_symbols_per_frame(self):
        return int((self.FSP_per_frame-1)*self.data_symbols + self.data_symbols_last)
    
    @property
    def symbol_oversample_rate(self):
        return self.fs/self.symbol_rate
    
    @property
    def samples_per_MFP(self):
        return int(self.MFP_symbols*self.symbol_oversample_rate)

    @property
    def samples_between_MFP(self):
        return int(self.frame_time*self.fs)

    @property
    def samples_per_FSP(self):
        return int(self.FSP_symbols*self.symbol_oversample_rate)
    
    @property
    def samples_between_FSP(self):
        return int((self.FSP_symbols+self.data_symbols)*self.symbol_oversample_rate)
    
    @property
    def samples_per_frame(self):
        return int(self.symbols_per_frame*self.symbol_oversample_rate)

    @property
    def samples_per_second(self):
        return self.fs
    
    # Print configuration for XM satellite object
    def print_config(self):
        print("samples per MFP = ",     self.samples_per_MFP)
        print("samples between MFP = ", self.samples_between_MFP)
        print("samples per FSP = ",     self.samples_per_FSP)
        print("samples between FSP = ", self.samples_between_FSP)
        print("samples per frame = ",   self.samples_per_frame)
        print("samples per second = ",  self.samples_per_second)

    class XM_interleaver:
        def __init__(self, buffer_size, step_size):
            self.buffer_size=buffer_size
            self.step_size=step_size
            self.buffer=np.zeros(buffer_size, dtype=float)
            self.step_indx=0
            self.switch_position=0 # 1 puts into buffer
        
        def advance(self, input_data):
            if self.switch_position:
                self.buffer=np.roll(self.buffer,1)
                output=self.buffer[0]
                self.buffer[0]=input_data
                self.step_indx+=1
                if self.step_indx==self.step_size:
                    self.switch_position=0
                    self.step_indx=0
                return output
            else:
                output=input_data
                self.step_indx+=1
                if self.step_indx==self.step_size:
                    self.switch_position=1
                    self.step_indx=1
                return output
