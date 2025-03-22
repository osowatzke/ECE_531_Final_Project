% Pluto SDR Configuration
fc = 2326.25e6;
fs = (2048+184)/(250e-6+22.45e-6);
N = 64*(2048+184);

% Create SDR Receiver
rx = sdrrx('Pluto',...
    'CenterFrequency',    fc,... fc,...
    'BasebandSampleRate', fs,... %fs,...
    'GainSource',         'AGC Slow Attack',...
    'OutputDataType',     'double',...
    'SamplesPerFrame',    N);

% Collect Desired Number of Samples
data = rx();

% Perform cross correlation
N = 2048;
cxy = data(1:(end-N)).*conj(data((N+1):end));
cxy = filter(ones(184,1),1,cxy);

% Truncate cross correlation output
N = 2048+184;
N = floor(length(cxy)/N)*N;
cxy = cxy(1:N);
N = 2048+184;
cxy = reshape(cxy,N,[]);

% Get the cross correlation power
cxyPwr = cxy.*conj(cxy);

% Average power across multiple frames
cxyPwr = mean(cxyPwr,2);

% Compute the course delay offset
[~, delay_offset] = max(cxyPwr);
delay_offset = delay_offset - 1;

% Compute the frequency offset
freq_offset = mean(angle(cxy(delay_offset+1,:)));
freq_offset = fs*freq_offset/(2*pi)/2048;

% Plot the cross correlation power
figure(1);
clf;
plot(0:(N-1),10*log10(cxyPwr));
xlim([0 2048+183]);
line(delay_offset*ones(1,2),ylim,'Color','red','LineStyle','--');
title(sprintf('Course Delay Offset = %d Samples : Freq Offset = %.f Hz', delay_offset, freq_offset));
xlabel('Sample Offset');
ylabel('dB');

% Account for frequency offset
n = (0:(length(data)-1)).';
freq_offset = freq_offset/fs;
freq_offset = freq_offset + 7/2048; % Apply Measured CFO
data = data.*exp(-1i*2*pi*freq_offset*n);

% Account for delay offset
I = delay_offset + 1 - 184/2;
if I < 1
    I = I + 2048 + 184;
end
data = data(I:end);
N = 2084 + 184;
N = floor(length(data)/N)*N;
data = data(1:N);
data = reshape(data,2048+184,[]);
data = data(1:2048,:);

% Get the Power of the OFDM output
Fdata = fftshift(fft(data));
Fdata = Fdata.*conj(Fdata);
Fdata = mean(Fdata,2);

% Estimate CFO
% [~,I] = min(abs(Fdata(1024+(-16:15))));
% I = I - 18;
% Fdata = circshift(Fdata,-I);

% Plot the resulting spectrum
figure(2);
clf;
N = 2048;
f = (0:(N-1))/N - 0.5;
f = f*fs*1e-6;
plot(f,db(Fdata));
xlabel('Frequency (MHz)')
ylabel('Amplitude (dB)')
