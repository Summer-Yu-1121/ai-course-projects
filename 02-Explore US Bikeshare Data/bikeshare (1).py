import time
import pandas as pd

CITY_DATA = {
    'chicago': 'chicago.csv',
    'new york city': 'new_york_city.csv',
    'washington': 'washington.csv',
}

VALID_MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'all']
VALID_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday',
              'friday', 'saturday', 'sunday', 'all']


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.
    Returns:
        city (str): 'chicago' | 'new york city' | 'washington'
        month (str): 'january'..'june' | 'all'
        day (str): 'monday'..'sunday' | 'all'
    """
    print("Hello! Let's explore some US bikeshare data!")

    # city
    while True:
        city = input("Choose a city (chicago, new york city, washington): ").strip().lower()
        if city in CITY_DATA:
            break
        print("Invalid city. Please enter: chicago, new york city, or washington.")

    # month
    while True:
        month = input("Choose a month (january - june) or 'all': ").strip().lower()
        if month in VALID_MONTHS:
            break
        print("Invalid month. Please enter january..june or 'all'.")

    # day
    while True:
        day = input("Choose a day (monday - sunday) or 'all': ").strip().lower()
        if day in VALID_DAYS:
            break
        print("Invalid day. Please enter monday..sunday or 'all'.")

    print('-' * 40)
    return city, month, day


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.
    Returns:
        df (pd.DataFrame): filtered dataframe with helper columns
    """
    df = pd.read_csv(CITY_DATA[city])

    # Parse datetime
    if 'Start Time' not in df.columns:
        raise KeyError("The dataset must contain a 'Start Time' column.")
    df['Start Time'] = pd.to_datetime(df['Start Time'], errors='coerce')
    df = df.dropna(subset=['Start Time'])

    # Helper columns
    df['month'] = df['Start Time'].dt.month        # 1..12
    df['day_of_week'] = df['Start Time'].dt.day_name()  # 'Monday'..
    df['hour'] = df['Start Time'].dt.hour          # 0..23

    # Filter month (only January..June per project)
    if month != 'all':
        months = ['january', 'february', 'march', 'april', 'may', 'june']
        month_num = months.index(month) + 1
        df = df[df['month'] == month_num]

    # Filter day
    if day != 'all':
        df = df[df['day_of_week'] == day.title()]

    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""
    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    if df.empty:
        print("No data available for the selected filters.")
        print("\nThis took %.4f seconds." % (time.time() - start_time))
        print('-' * 40)
        return

    # Most common month (print as name)
    common_month_num = int(df['month'].mode()[0])
    month_name = pd.to_datetime(str(common_month_num), format='%m').month_name()
    print(f"Most Common Month: {month_name}")

    # Most common day of week
    common_day = df['day_of_week'].mode()[0]
    print(f"Most Common Day of Week: {common_day}")

    # Most common start hour
    common_hour = int(df['hour'].mode()[0])
    print(f"Most Common Start Hour: {common_hour}")

    print("\nThis took %.4f seconds." % (time.time() - start_time))
    print('-' * 40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""
    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    if df.empty:
        print("No data available for the selected filters.")
        print("\nThis took %.4f seconds." % (time.time() - start_time))
        print('-' * 40)
        return

    # Most common start station
    if 'Start Station' in df.columns and not df['Start Station'].empty:
        print("Most Common Start Station:", df['Start Station'].mode()[0])
    else:
        print("Start Station data not available.")

    # Most common end station
    if 'End Station' in df.columns and not df['End Station'].empty:
        print("Most Common End Station:", df['End Station'].mode()[0])
    else:
        print("End Station data not available.")

    # Most frequent combination
    if {'Start Station', 'End Station'}.issubset(df.columns):
        routes = df['Start Station'].astype(str) + " -> " + df['End Station'].astype(str)
        print("Most Common Route:", routes.mode()[0])
    else:
        print("Route combination cannot be computed due to missing columns.")

    print("\nThis took %.4f seconds." % (time.time() - start_time))
    print('-' * 40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""
    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    if df.empty or 'Trip Duration' not in df.columns:
        print("Trip Duration data not available for the selected filters.")
        print("\nThis took %.4f seconds." % (time.time() - start_time))
        print('-' * 40)
        return

    total_travel = df['Trip Duration'].sum()
    mean_travel = df['Trip Duration'].mean()

    print(f"Total Travel Time: {int(total_travel)} seconds")
    print(f"Average Travel Time: {mean_travel:.2f} seconds")

    print("\nThis took %.4f seconds." % (time.time() - start_time))
    print('-' * 40)


def user_stats(df):
    """Displays statistics on bikeshare users."""
    print('\nCalculating User Stats...\n')
    start_time = time.time()

    if df.empty:
        print("No data available for the selected filters.")
        print("\nThis took %.4f seconds." % (time.time() - start_time))
        print('-' * 40)
        return

    # User types
    if 'User Type' in df.columns:
        print("Counts of User Types:")
        print(df['User Type'].value_counts())
    else:
        print("User Type data not available.")

    # Gender (Washington has none)
    if 'Gender' in df.columns:
        print("\nCounts of Gender:")
        print(df['Gender'].value_counts(dropna=True))
    else:
        print("\nNo gender data for this city.")

    # Birth year
    if 'Birth Year' in df.columns:
        valid_birth_year = df['Birth Year'].dropna()
        if not valid_birth_year.empty:
            print("\nEarliest Birth Year:", int(valid_birth_year.min()))
            print("Most Recent Birth Year:", int(valid_birth_year.max()))
            print("Most Common Birth Year:", int(valid_birth_year.mode()[0]))
        else:
            print("\nBirth Year column exists but all values are NaN.")
    else:
        print("\nNo birth year data for this city.")

    print("\nThis took %.4f seconds." % (time.time() - start_time))
    print('-' * 40)


def display_raw_data(df):
    """
    Ask the user if they want to see 5 rows of raw data, repeatedly.
    """
    start = 0
    while True:
        show = input("\nWould you like to see 5 rows of raw data? Enter yes or no: ").strip().lower()
        if show not in ['yes', 'y', 'no', 'n']:
            print("Please answer with yes/y or no/n.")
            continue
        if show in ['no', 'n']:
            break

        end = start + 5
        print(df.iloc[start:end])
        start = end

        if start >= len(df):
            print("\nNo more data to display.")
            break


def main():
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)

        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        display_raw_data(df)

        restart = input("\nWould you like to restart? Enter yes or no.\n").strip().lower()
        if restart != 'yes':
            break


if __name__ == "__main__":
    main()