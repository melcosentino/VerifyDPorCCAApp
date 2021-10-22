import numpy as np
import scipy.signal as sig
import soundfile as sf
import pathlib
import zipfile
import matplotlib.pyplot as plt
import datetime
import pandas as pd


LOW_FREQ = 120000
HIGH_FREQ = 150000
FILTER_ORDER = 4
P_REF = 1.0
SAMPLES_SPECTROGRAM = 5760


class CTSignal:
    def __init__(self,  ct):
        """
        Object to manage the CT signal
        """
        # Get the file path name
        wav_file_path = pathlib.Path(ct.filename[0])
        if '.zip' in str(wav_file_path):
            zip_file = zipfile.ZipFile(wav_file_path.parent)
            wav_file_path = zip_file.open(wav_file_path.name)

        self.continuous = True
        # Different processing if soundtrap HF or continous recording
        if '.wav' in wav_file_path.name:
            self.start_sample = ct.start_sample.iloc[0] - SAMPLES_SPECTROGRAM
            self.end_sample = ct.start_sample.iloc[-1] + SAMPLES_SPECTROGRAM
        elif '.dwv' in wav_file_path.name:
            self.start_sample = ct.start_sample.iloc[0]
            self.end_sample = ct.start_sample.iloc[-1] + int(ct.duration_samples.iloc[-1])
            self.continuous = False
        else:
            raise FileNotFoundError('This extension does not exist. File %s' % wav_file_path)

        # Read the file
        signal, self.fs = sf.read(wav_file_path, start=int(self.start_sample), stop=int(self.end_sample))

        # Reduce the DC noise
        dc_noise = np.mean(signal)
        self.s = signal - dc_noise

        # Compute the time scale
        duration = len(self.s) / self.fs
        self.t = np.arange(0.0, duration, 1 / self.fs)

        self.filtered_signal = self.s

        self.ct = ct
        self.ct.datetime = pd.to_datetime(self.ct.datetime)
        self.ct.datetime = self.ct.datetime - self.ct.datetime.iloc[0]

    def prepare_signal(self):
        """
        Prepare the signal for the spectrogram (filter!)
        """
        sos = sig.butter(FILTER_ORDER, [LOW_FREQ, HIGH_FREQ], 'bandpass', fs=self.fs, output='sos')
        self.filtered_signal = sig.sosfilt(sos, self.s)

    def spectrogram(self, nfft=512, db=True, noverlap=0):
        """
        Return the spectrogram of the signal (entire file)
        Parameters
        ----------
        db : bool
            If set to True the result will be given in db, otherwise in uPa^2
        nfft : int
            Length of the fft window in samples. Power of 2.
        noverlap: int
            Number of frames to overlap
        Returns
        -------
        freq, t, sxx
        """
        real_size = self.filtered_signal.size
        if real_size < nfft:
            s = self._fill_or_crop(n_samples=nfft)
        else:
            s = self.filtered_signal
        window = sig.get_window('hann', nfft)
        freqs, time, sxx = sig.spectrogram(s, fs=self.fs, nfft=nfft, window=window, scaling='spectrum', noverlap=noverlap)

        if db:
            sxx = 10 * np.log10(sxx / P_REF ** 2)
        return freqs, time, sxx

    def plot_spectrogram(self, nfft=512, db=True, noverlap=0):
        freqs, time, sxx = self.spectrogram(nfft, db, noverlap)
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
        ax1.plot(self.t, self.filtered_signal)
        ax2.pcolormesh(time, freqs, sxx, shading='auto', cmap='viridis')
        ax2.set_title('Spectrogram')
        ax2.set_xlabel('Time [s]')
        ax2.set_ylabel('Frequency [Hz]')
        plt.show()

        if not self.continuous:
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
            end_time = (self.ct.datetime.iloc[-1] + datetime.timedelta(microseconds=self.ct.duration_us.iloc[-1])).total_seconds()
            total_time = np.arange(0, end_time, step=(nfft-noverlap)/self.fs)
            sxx_total = np.zeros((len(freqs), len(total_time)))
            start_sample = self.ct.start_sample.iloc[0]
            for idx, c in self.ct.iterrows():
                c_time = np.arange(0.0, c.duration_samples) * 1/self.fs + c.datetime.total_seconds()
                c_start_sample = c.start_sample - start_sample
                c_signal = self.filtered_signal[c_start_sample: c_start_sample + int(c.duration_samples)]
                c_dwv_time = self.t[c_start_sample: c_start_sample + int(c.duration_samples)]
                sxx_mask = np.where((time >= c_dwv_time[0]) & (time <= c_dwv_time[-1]))[0]
                time_mask = np.argwhere(total_time >= c_time[0])[0][0]
                time_mask = np.arange(time_mask, time_mask+len(sxx_mask))
                sxx_total[:, time_mask] = sxx[:, sxx_mask]
                ax1.plot(c_time, c_signal)
            sxx_total[sxx_total == 0] = np.nan
            ax2.pcolormesh(total_time, freqs, sxx_total, shading='auto', cmap='viridis')
            ax2.set_title('Spectrogram')
            ax2.set_xlabel('Time [s]')
            ax2.set_ylabel('Frequency [Hz]')
            plt.show()



    def _fill_or_crop(self, n_samples):
        """
        Crop the signal to the number specified or fill it with 0 values in case it is too short
        Parameters
        ----------
        n_samples : int
            Number of desired samples
        """
        if self.filtered_signal.size >= n_samples:
            s = self.filtered_signal[0:n_samples]
        else:
            nan_array = np.full((n_samples,), 0)
            nan_array[0:self.filtered_signal.size] = self.filtered_signal
            s = nan_array
        return s
