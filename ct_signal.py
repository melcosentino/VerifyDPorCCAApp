import numpy as np
import scipy.signal as sig
import soundfile as sf


LOW_FREQ = 10
HIGH_FREQ = 200000
FILTER_ORDER = 4
P_REF = 1.0


class CTSignal:
    def __init__(self, wav_file_path, start, end):
        """
        Object to manage the CT signal
        :param wav_file_path: str or Path
        :param start: sample there the CT starts
        :param end: sample where the CT ends
        """
        # Read the file
        signal, self.fs = sf.read(wav_file_path, start=int(start), stop=int(end))

        # Reduce the DC noise
        dc_noise = np.mean(signal)
        self.s = signal - dc_noise

        # Compute the time scale
        duration = len(self.s) / self.fs
        self.t = np.arange(0.0, duration, 1 / self.fs)

        self.filtered_signal = self.s

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
        mode : string
            If set to 'fast', the signal will be zero padded up to the closest power of 2
        force_calc : bool
            Set to True if the computation has to be forced
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
