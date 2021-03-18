import numpy as np
import scipy.signal as sig


LOW_FREQ = 10
HIGH_FREQ = 50000

class CTSignal:
    def __init__(self, soundfile, start, end):
        """
        Object to manage the CT signal
        :param soundfile: soundfile object, where the audio is stored
        :param start: sample there the CT starts
        :param end: sample where the CT ends
        """
        soundfile.seek(int(start))
        signal = soundfile.read(int(end) - int(start))
        soundfile.close()
        mean_sig = sum(signal) / len(signal)

        self.s = signal - mean_sig
        self.fs = soundfile.samplerate
        self.sxx = None
        self.psd = None
        self.freq = None

        duration = len(self.s) / self.fs
        self.t = np.arange(0.0, duration, 1 / self.fs)

    def prepare_signal(self):
        """
        Prepare the signal for the spectrogram (filter!)
        """
        sos = sig.butter(LOW_FREQ, HIGH_FREQ, 'hp', fs=self.fs, output='sos')
        self.filtered_signal = sig.sosfilt(sos, self.s)

    def spectrogram(self, nfft=512, scaling='density', db=True, mode='fast', force_calc=False):
        """
        Return the spectrogram of the signal (entire file)
        Parameters
        ----------
        db : bool
            If set to True the result will be given in db, otherwise in uPa^2
        nfft : int
            Length of the fft window in samples. Power of 2.
        scaling : string
            Can be set to 'spectrum' or 'density' depending on the desired output
        mode : string
            If set to 'fast', the signal will be zero padded up to the closest power of 2
        force_calc : bool
            Set to True if the computation has to be forced
        Returns
        -------
        freq, t, sxx
        """
        if force_calc:
            self._spectrogram(nfft=nfft, scaling=scaling, mode=mode)
        if db:
            sxx = self.to_db(self.sxx, ref=1.0, square=False)
        return sxx

    def to_db(self, wave, ref=1.0, square=False):
        """
        Compute the db from the upa signal
        Parameters
        ----------
        wave : numpy array
            Signal in upa
        ref : float
            Reference pressure
        square : boolean
            Set to True if the signal has to be squared
        """
        if square:
            db = 10 * np.log10(wave ** 2 / ref ** 2)
        else:
            db = 10 * np.log10(wave / ref ** 2)
        return db

    def _spectrogram(self, nfft=512, scaling='density', mode='fast'):
        """
        Computes the spectrogram of the signal and saves it in the attributes
        Parameters
        ----------
        nfft : int
            Length of the fft window in samples. Power of 2.
        scaling : string
            Can be set to 'spectrum' or 'density' depending on the desired output
        mode : string
            If set to 'fast', the signal will be zero padded up to the closest power of 2
        Returns
        -------
        None
        """
        real_size = self.filtered_signal.size
        if self.filtered_signal.size < nfft:
            s = self._fill_or_crop(n_samples=nfft)
        else:
            if mode == 'fast':
                # Choose the closest power of 2 to clocksize for faster computing
                optim_len = int(2 ** np.ceil(np.log2(real_size)))
                # Fill the missing values with 0
                s = self._fill_or_crop(n_samples=optim_len)
            else:
                s = self.filtered_signal
        window = sig.get_window('hann', nfft)
        freq, t, sxx = sig.spectrogram(s, fs=self.fs, nfft=nfft,
                                          window=window, scaling=scaling)
        low_freq = 0
        self.freq = freq[low_freq:]
        n_bins = int(np.floor(real_size / (nfft * 7 / 8)))
        self.sxx = sxx[low_freq:, 0:n_bins]
        self.sxx_t = t[0:n_bins]

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

    def reset_spectro(self):
        """
        Reset the spectrogram parameters
        """
        self.sxx = None
        self.freq = None
        self.sxx_t = None
