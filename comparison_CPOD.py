import pandas as pd
import datetime


def positive_porpoise_minute(df, date_column, class_column, end_column, hq, lq, start_minute=None, end_minute=None):
    """
    Returns the number of click trains per minute
    :param df: DataFrame
        Output DataFrame from pyporcc AFTER classificatio
    :param date_column: string
        Name of the column where the datetime information is
    :param class_column: string
        Name of the column where the classification output of clicktrains
    :param end_column: string
        Name of the column where the the information about the end of the click train is
    :param hq: string or int
        Name of high quality click train in the column class_column
    :param lq: string or int
        Name of low quality click train in the column class_column
    :return: DataFrame with all the minutes and True of False depending if it is positive porpoise minute (PPM)
    """
    df['minutes_ppm'] = df[date_column]
    df['minutes_ppm'] = df['minutes_ppm'].dt.floor('min')
    df_strict = df[df[class_column] == hq][['minutes_ppm', end_column]]
    df_relaxed = df[(df[class_column] == lq) | (df[class_column] == hq)][['minutes_ppm', end_column]]
    df_strict = add_middle_minutes(df_strict, end_column)
    df_relaxed = add_middle_minutes(df_relaxed, end_column)

    if start_minute is None:
        start_minute = min(df_strict['minutes_ppm'].min(), df_relaxed['minutes_ppm'].min())
    if end_minute is None:
        end_minute = max(df_strict['minutes_ppm'].max(), df_relaxed['minutes_ppm'].max())
    minutes_idxs = pd.date_range(start_minute, end_minute, freq='1min')
    ppm_df = pd.DataFrame(columns=['ppm_strict', 'ppm_relaxed'], index=minutes_idxs)
    ppm_df['ppm_strict'] = 0
    ppm_df['ppm_relaxed'] = 0
    ppm_df.loc[df_strict.minutes_ppm.unique(), 'ppm_strict'] = 1
    ppm_df.loc[df_relaxed.minutes_ppm.unique(), 'ppm_relaxed'] = 1

    return ppm_df.astype(int)


def add_middle_minutes(df, end_column):
    """
    Add to the data frame rows between the start and the end of every click train. (i.e. if a click train starts at
    minute 1 and finishes at minute 3, add 2 as a row in the column minutes_ppm)
    :param df: dataframe with all the click trains. It needs to include minutes_ppm as a column.
    :param end_column: string. Name of the column where the end of the click train is (in datetime)
    :return:
    """
    df.reset_index(inplace=True, drop=True)
    for idx, minute_row in df.iterrows():
        next_min = minute_row['minutes_ppm'] + datetime.timedelta(minutes=1)
        while next_min <= minute_row[end_column]:
            df.loc[len(df)] = [next_min, minute_row[end_column]]
            next_min += datetime.timedelta(minutes=1)
    df = df.sort_values('minutes_ppm', ignore_index=True)
    return df


def add_end_ct(df, df_info):
    """
    Add a column to df with the timestamp of the last click of the click train
    :param df: dataframe with click trains
    :param df_info: dataframe with the clicks corresponding to the click trains
    """
    df['EndCT'] = None
    for new_ct, info_ct in df_info.groupby('NewCT'):
        try:
            df.loc[df['NewCT'] == new_ct, 'EndCT'] = info_ct.iloc[-1]['datetime']
        except IndexError:
            print('This Clicks file does not contain the CT number %s. '
                  'Please check if the clicks belong to the same project' % new_ct)

    df['EndCT'] = pd.to_datetime(df['EndCT'])
    return df


def select_validation(CTInfo_path, CTrains_path, CPOD_validated_path, start_date=None, end_date=None):
    """
    Select which CT of DPorCCA have to be validated.
    :param CTInfo_path: Path to the file with all the Clicks present in the Click trains (AllClicks.csv)
    :param CTrains_path: Path to the file with all the Click Trains information (AllCTInfo.csv)
    :param CPOD_validated_path: Path to *.txt file with all the ClickTrains output from CPOD.exe
    :return: validation_minutes, Verify. The first is a dataset with all the ppm of the two methods. Second one
    is a list of all the CT that have to be validated
    """
    if type(start_date) == str:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
    if type(end_date) == str:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    CTInfo = pd.read_csv(CTInfo_path, parse_dates=['Date'], infer_datetime_format=True)
    CTrains = pd.read_csv(CTrains_path, parse_dates=['datetime'], infer_datetime_format=True)
    AllCTInfo = add_end_ct(CTInfo, CTrains)
    DPorCCA_ppm = positive_porpoise_minute(AllCTInfo, class_column='CTType', end_column='EndCT',
                                           date_column='Date', hq='NBHF', lq='LQ-NBHF',
                                           start_minute=start_date, end_minute=end_date)

    # FROM CPOD TO COMPARISON TABLE
    CPOD_validated = pd.read_table(CPOD_validated_path, parse_dates=['Time'], infer_datetime_format=True, dayfirst=True)
    CPOD_validated.loc[CPOD_validated['TrClass'] == "Low", 'CTType'] = 'LQ-NBHF'
    CPOD_validated.loc[
        ((CPOD_validated['TrClass'] == "High") | (CPOD_validated['TrClass'] == 'Mod')), 'CTType'] = 'NBHF'
    CPOD_validated['EndTr'] = pd.to_timedelta(CPOD_validated['TrDur_us'], 'us') + CPOD_validated['Time']
    CPOD_ppm = positive_porpoise_minute(CPOD_validated, class_column='CTType', date_column='Time',
                                        end_column='EndTr', hq='NBHF', lq='LQ-NBHF',
                                        start_minute=start_date, end_minute=end_date)

    validation_minutes = DPorCCA_ppm.merge(CPOD_ppm, suffixes=['_DPorCCA', '_CPOD'], left_index=True, right_index=True)

    # Assume all the DPorCCA CT have to be validated
    validation_minutes['validation'] = 1
    validation_minutes.loc[(validation_minutes['ppm_relaxed_DPorCCA'] == 0, 'validation')] = 0

    # Check all the minutes that are positive in a 3-min window in validated cpod
    # Assume these ones are then already validated
    for i, row in validation_minutes.iterrows():
        if row.loc['validation'] == 1:
            # For each positive minute, check the minute and the previous and the following in CPOD.
            # because they are all validated we only look at relaxed criteria
            i_start = i - datetime.timedelta(minutes=1)
            i_end = i + datetime.timedelta(minutes=1)
            cpod_3min_window = validation_minutes.loc[i_start:i_end]
            # If the 3-min window is at some point positive, that minute does not have to be validated
            if cpod_3min_window['ppm_relaxed_CPOD'].sum() > 0:
                validation_minutes.loc[i, 'validation'] = 0

    AllCTInfo['Verified'] = 0
    AllCTInfo['Validation'] = 0
    for i, row in validation_minutes.iterrows():
        if row.loc['validation'] == 1:
            next_min = i + datetime.timedelta(minutes=2)
            mask_start = (AllCTInfo.Date >= i) & (AllCTInfo.Date <= next_min)    # CT that start in the minute
            mask_end = (AllCTInfo.EndCT >= i) & (AllCTInfo.EndCT <= next_min)    # CT which end in the minute
            mask_during = (AllCTInfo.Date <= i) & (AllCTInfo.EndCT >= next_min)  # CT that start before and end after
            mask = mask_start | mask_end | mask_during
            AllCTInfo.loc[mask, 'Validation'] = 1

    return validation_minutes, AllCTInfo[AllCTInfo.Validation == 1]


def compare_validated(validation, validated_CT, validated_CT_info):
    """
    Compare the output of both systems
    :param validation:
    :param validated_CT:
    :param validated_CT_info:
    """
    validated_CT['PorpoisePresence'] = 0
    validated_CT.loc[(validated_CT['Corr'] == 1) & (validated_CT['CTType'] == 'Noise'), 'PorpoisePresence'] = 0
    validated_CT.loc[(validated_CT['Corr'] == 1) & (validated_CT['CTType'] != 'Noise'), 'PorpoisePresence'] = 1
    validated_CT.loc[(validated_CT['Corr'] == 0) & (validated_CT['CTType'] == 'Noise'), 'PorpoisePresence'] = 1
    validated_CT.loc[(validated_CT['Corr'] == 0) & (validated_CT['CTType'] != 'Noise'), 'PorpoisePresence'] = 0
    validated_CT = add_end_ct(validated_CT, validated_CT_info)
    ppm_validated = positive_porpoise_minute(validated_CT, date_column='Date', class_column='PorpoisePresence',
                                             end_column='EndCT', hq=1, lq=1)
    ppm = ppm_validated['ppm_strict']
    validation = validation.merge(ppm, left_index=True, right_index=True)

    return validation


if __name__ == "__main__":
    CTInfo_path = 'CTInfo.csv'
    CTrains_path = 'CTrains.csv'
    CPOD_path = 'CPOD.txt'
    CTInfo_validated_path = 'VerifyCT_cpod.csv'
    v = select_validation(CTInfo_path, CTrains_path, CPOD_path)
    v_CT = pd.read_csv(CTInfo_validated_path, parse_dates=['Date'], infer_datetime_format=True)
    v_CT_info = pd.read_csv(CTrains_path, parse_dates=['datetime'], infer_datetime_format=True)
    validation = compare_validated(v, v_CT, v_CT_info)
    validation.to_csv('validation_final.csv')
