import pandas as pd


def positive_porpoise_minute(df, date_column, class_column, end_column, hq, lq):
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
    df['minutes_ppm'] = df['minutes_ppm'].dt.round('min')
    start_minute = df['minutes_ppm'].min()
    end_minute = df['minutes_ppm'].max()
    minutes_idxs = pd.date_range(start_minute, end_minute, freq='1min')
    ppm_df = pd.DataFrame(columns=['ppm_strict', 'ppm_relaxed'], index=minutes_idxs)
    ppm_df['ppm_strict'] = 0
    ppm_df['ppm_relaxed'] = 0
    # Select all the different minutes in the dataframe
    minutes_list = df.minutes_ppm.unique()
    for min_idx, minute in enumerate(minutes_list):
        all_min_clicks = df.loc[df['minutes_ppm'] == minute]
        # If the last CT of the minute is goes to the next minute, add the next minute as ppm
        last_ct = all_min_clicks.iloc[-1]
        if last_ct.loc[end_column] > minute:
            if min_idx < len(minutes_list) - 1:
                ppm_df.at[minutes_list[min_idx + 1], 'ppm_strict'] = 1
                ppm_df.at[minutes_list[min_idx + 1], 'ppm_relaxed'] = 1
        # In case there is any click train starting at that specific minute, add it as ppm
        ppm_df.at[minute, 'ppm_strict'] = (all_min_clicks[class_column] == hq).any() or ppm_df.loc[minute, 'ppm_strict']
        ppm_df.at[minute, 'ppm_relaxed'] = (((all_min_clicks[class_column] == hq) |
                                             (all_min_clicks[class_column] == lq)).any()) or ppm_df.loc[
                                               minute, 'ppm_strict']
    return ppm_df.astype(int)


def add_end_ct(df, df_info):
    df['EndCT'] = None
    for idx, row in df.iterrows():
        info_ct = df_info.loc[df_info['CT'] == row.loc['CTNum']]
        df['EndCT'] = info_ct.iloc[-1]['datetime']

    return df


def select_validation(CTInfo_path, CTrains_path, CPOD_validated_path):
    """
    Create a
    :param AllCTInfo_path:
    :param CPOD_validated_path:
    :return:
    """
    CTInfo = pd.read_csv(CTInfo_path, parse_dates=['Date'], infer_datetime_format=True)
    CTrains = pd.read_csv(CTrains_path, parse_dates=['datetime'], infer_datetime_format=True)
    AllCTInfo = add_end_ct(CTInfo, CTrains)
    DPorCCA_ppm = positive_porpoise_minute(AllCTInfo, class_column='Species', end_column='EndCT',
                                           date_column='Date', hq='NBHF', lq='LQ-NBHF')

    # FROM CPOD TO COMPARISON TABLE
    CPOD_validated = pd.read_csv(CPOD_validated_path, parse_dates=['Time'], infer_datetime_format=True, dayfirst=True)
    CPOD_validated.loc[CPOD_validated['TrClass'] == "Low", 'Species'] = 'LQ-NBHF'
    CPOD_validated.loc[
        ((CPOD_validated['TrClass'] == "High") | (CPOD_validated['TrClass'] == 'Mod')), 'Species'] = 'NBHF'
    CPOD_validated['EndTr'] = pd.to_timedelta(CPOD_validated['TrDur_us'], 'us') + CPOD_validated['Time']
    CPOD_ppm = positive_porpoise_minute(CPOD_validated, class_column='Species', date_column='Time',
                                        end_column='EndTr', hq='NBHF', lq='LQ-NBHF')

    validation_minutes = DPorCCA_ppm.merge(CPOD_ppm, suffixes=['_DPorCCA', '_CPOD'], left_index=True, right_index=True)
    validation_minutes['validation'] = 1
    validation_minutes.loc[(validation_minutes['ppm_strict_DPorCCA'] == 1) &
                           (validation_minutes['ppm_strict_CPOD'] == 1), 'validation'] = 0
    validation_minutes.loc[(validation_minutes['ppm_relaxed_DPorCCA'] == 0) &
                           (validation_minutes['ppm_relaxed_CPOD'] == 0), 'validation'] = 0

    return validation_minutes


def compare_validated(validation, validated_CT, validated_CT_info):
    validated_CT['PorpoisePresence'] = 0
    validated_CT.loc[(validated_CT['Corr'] == 1) & (validated_CT['Species'] == 'Non-NBHF'), 'PorpoisePresence'] = 0
    validated_CT.loc[(validated_CT['Corr'] == 1) & (validated_CT['Species'] != 'Non-NBHF'), 'PorpoisePresence'] = 1
    validated_CT.loc[(validated_CT['Corr'] == 0) & (validated_CT['Species'] == 'Non-NBHF'), 'PorpoisePresence'] = 1
    validated_CT.loc[(validated_CT['Corr'] == 0) & (validated_CT['Species'] != 'Non-NBHF'), 'PorpoisePresence'] = 0
    validated_CT = add_end_ct(validated_CT, validated_CT_info)
    ppm_validated = positive_porpoise_minute(validated_CT, date_column='Date', class_column='PorpoisePresence',
                                             end_column='EndCT', hq=1, lq=1)
    ppm = ppm_validated['ppm_strict']
    validation = validation.merge(ppm, left_index=True, right_index=True)

    return validation


if __name__ == "__main__":

    CTInfo_path = 'CTInfo.csv'
    CTrains_path = 'CTrains.csv'
    CPOD_path = 'CPOD_validation.csv'
    CTInfo_validated_path = 'CTInfo_val.csv'
    v = select_validation(CTInfo_path, CTrains_path, CPOD_path)
    v_CT = pd.read_csv(CTInfo_validated_path, parse_dates=['Date'], infer_datetime_format=True)
    v_CT_info = pd.read_csv(CTrains_path, parse_dates=['datetime'], infer_datetime_format=True)
    validation = compare_validated(v, v_CT, v_CT_info)
    validation.to_csv('validation_final.csv')
