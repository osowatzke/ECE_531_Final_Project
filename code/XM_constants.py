import numpy as np
import matplotlib.pyplot as plt
class XM_sat:
    def __init__(self, fs=1.64e6, oversample=1):
        self.fs=fs
        self.symbol_rate=1.64e6
        self.frame_time=.432
        self.MFP_symbols=64
        self.FSP_symbols=32
        self.Data_symbols=3424
        self.Data_symbols_last=3264 #note, last FSP has shorter Data_symbols + PAD
        self.PAD_symbols=96
        self.FSP_per_frame=205
        self.samples_per_frame=int(self.MFP_symbols+self.FSP_per_frame*(self.FSP_symbols+self.Data_symbols)+\
            self.PAD_symbols-(self.Data_symbols-self.Data_symbols_last))
        #assuming starts at 1
        FSP = -np.array([-1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,
                        1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1])
        self.FSP=FSP*(1+1j)
        MFP = np.array([-1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, -1, 1, -1, -1,
                         1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1,
                         1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1, 1, -1,
                         -1, -1, 1, -1, 1, 1])
        self.MFP=MFP*(1+1j)
        self.samples_between_frames=self.samples_per_frame*fs/self.symbol_rate
        self.samples_between_FSP=int((self.Data_symbols+self.FSP_symbols)*fs/self.symbol_rate)

    def get_freq_est(self, data, debug=False):
        span=int(self.samples_between_FSP)
        corr_out=np.correlate(data, self.FSP)
        max_FSP=np.argmax(np.abs(corr_out))
        print("FIRST FSP found at ", max_FSP)
        # take 4th power to find freq
        temp_data_sq=data*data
        freq_fft=np.abs(np.fft.fft(temp_data_sq*temp_data_sq))
        max_freq_bin=np.argmax(freq_fft)
        print("freq bin = ", max_freq_bin)
        freq_per_bin = self.fs/(4*span) #power of 4 with span
        bin_offset=self.interp(freq_fft[max_freq_bin-1], freq_fft[max_freq_bin], freq_fft[max_freq_bin+1])
        course_freq_est=(max_freq_bin+bin_offset)*freq_per_bin
        print ("Course freq estimate = ", course_freq_est)
        if (debug):
            t=np.arange(span)/self.fs
            temp_data=data*np.exp(-1j*2*np.pi*course_freq_est*t)
            plt.plot(np.angle(temp_data),'b.')
            plt.show()
        return(course_freq_est)
    def interp(self, ym1,y0,yp1):
        p = (yp1 - ym1)/(2*(2*y0 - yp1 - ym1)); #position
        y = y0 - 0.25*(ym1-yp1)*p; #height
        return(p)


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
