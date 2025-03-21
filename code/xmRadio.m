% Pluto SDR Configuration
fc = 2338.7575e6;
fs = 12.5e6;
N = 2^16;

% Create SDR Receiver
rx = sdrrx('Pluto',...
    'CenterFrequency',    fc,...
    'BasebandSampleRate', fs,...
    'GainSource',         'AGC Slow Attack',...
    'SamplesPerFrame',    N);

% Collect Desired Number of Samples
data = double(rx());

% Create frequency axis
f = (0:(N-1))/N;
f = f - 0.5;
f = fs*f + fc;

% Plot the spectrum
figure(1); clf;
plot(f, fftshift(db(fft(data))))

% Create a waterfall plot
figure(2); clf;
spectrogram(data,4096,2048,16384,'centered');
clim([20 60]);