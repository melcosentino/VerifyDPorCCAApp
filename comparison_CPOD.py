import pandas as pd


def positive_porpoise_minute(df, date_column, class_column, hq, lq):
    """
    Returns the number of click trains per minute

    Parameters
    ----------
    df : DataFrame
        Output DataFrame from pyporcc AFTER classification
    Returns
    -------
    DataFrame with all the minutes and True of False depending if it is positive porpoise minute (PPM)
    """
    df['minutes_ppm'] = df[date_column]
    df['minutes_ppm'] = df['minutes_ppm'].dt.round('min')
    start_minute = df['minutes_ppm'].min()
    end_minute = df['minutes_ppm'].max()
    minutes_idxs = pd.date_range(start_minute, end_minute, freq='1min')
    ppm_df = pd.DataFrame(columns=['ppm_strict', 'ppm_relaxed'], index=minutes_idxs)
    ppm_df['ppm_strict'] = 0
    ppm_df['ppm_relaxed'] = 0
    for minute in df.minutes_ppm.unique():
        all_min_clicks = df.loc[df['minutes_ppm'] == minute]
        ppm_df.at[minute, 'ppm_strict'] = (all_min_clicks[class_column] == hq).any()
        ppm_df.at[minute, 'ppm_relaxed'] = ((all_min_clicks[class_column] == hq) |
                                            (all_min_clicks[class_column] == lq)).any()
    return ppm_df.astype(int)


def select_validation(AllCTInfo_path, CPOD_validated_path):
    AllCTInfo = pd.read_csv(AllCTInfo_path, parse_dates=['Date'], infer_datetime_format=True)
    # AllNBHF = AllCTInfo[(AllCTInfo.Species == 'NBHF') | (AllCTInfo.Species == 'LQ-NBHF')]
    DPorCCA_ppm = positive_porpoise_minute(AllCTInfo, class_column='Species',
                                           date_column='Date', hq='NBHF', lq='LQ-NBHF')

    # FROM CPOD TO COMPARISON TABLE
    CPOD_validated = pd.read_csv(CPOD_validated_path, parse_dates=['Time'], infer_datetime_format=True, dayfirst=True)
    CPOD_validated.loc[CPOD_validated['TrClass'] == "Low", 'Species'] = 'LQ-NBHF'
    CPOD_validated.loc[((CPOD_validated['TrClass'] == "High") | (CPOD_validated['TrClass'] == 'Mod')), 'Species'] = 'NBHF'
    CPOD_ppm = positive_porpoise_minute(CPOD_validated, class_column='Species', date_column='Time',
                                        hq='NBHF', lq='LQ-NBHF')

    validation_minutes = DPorCCA_ppm.merge(CPOD_ppm, suffixes=['_DPorCCA', '_CPOD'], left_index=True, right_index=True)
    validation_minutes['validation'] = 1
    validation_minutes.loc[(validation_minutes['ppm_strict_DPorCCA'] == 1) &
                           (validation_minutes['ppm_strict_CPOD'] == 1), 'validation'] = 0
    validation_minutes.loc[(validation_minutes['ppm_relaxed_DPorCCA'] == 0) &
                           (validation_minutes['ppm_relaxed_CPOD'] == 0), 'validation'] = 0

    return validation_minutes


if __name__ == "__main__":
    validation = select_validation('CTInfo.csv', 'CPOD_validated.csv')
    validation.to_csv('validation.csv')
