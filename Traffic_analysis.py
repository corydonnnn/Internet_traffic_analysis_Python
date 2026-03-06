import pandas as pd
import os
import matplotlib.pyplot as plt


# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------

def ensure_dir(directory):
    """Create directory if it does not exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)


# ----------------------------
# DATA LOADING & CLEANING
# ----------------------------

def load_and_clean(file_path):
    """
    Load dataset and perform basic cleaning
    """
    df = pd.read_csv(file_path)

    # Health check
    print(df.head(), '\n')
    print(df.tail(), '\n')
    print(df.shape, '\n')
    print(df.info(), '\n')
    print(df.describe(), '\n')

    # Missing values
    print("Missing values:\n", df.isnull().sum(), '\n')

    # Remove corrupt rows
    df = df.dropna(subset=['user_id', 'tariff_plan', 'region'])

    # Convert to numeric
    df['plan_limit_gb'] = pd.to_numeric(df['plan_limit_gb'], errors='coerce')
    df['traffic_gb_used'] = pd.to_numeric(df['traffic_gb_used'], errors='coerce')

    df['traffic_gb_used'] = df['traffic_gb_used'].fillna(0)

    # Create new column
    df['over_limit'] = df['traffic_gb_used'] > df['plan_limit_gb']

    return df


# ----------------------------
# REPORT FUNCTIONS
# ----------------------------

def report_subscribers_by_region(df):
    report = df.groupby('region').size().rename('records_count').reset_index()
    report = report.sort_values('records_count', ascending=False)
    print("\n--- Report 1: Number of Subscribers by Region ---\n")
    print(report.to_string(index=False))
    ensure_dir('reports')
    report.to_csv('reports/subscribers_by_region.csv', index=False)
    return report


def report_avg_traffic_target_regions(df):
    target_regions = ['Bishkek', 'Osh']
    df_filtered = df[df['region'].isin(target_regions)].copy()
    report = df_filtered.groupby('tariff_plan', as_index=False)['traffic_gb_used'].mean()
    report = report.rename(columns={'traffic_gb_used': 'avg_traffic_gb_used'})
    report = report.sort_values('avg_traffic_gb_used', ascending=False)
    print("\n--- Report 2: Avg Traffic in Target Regions ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/avg_traffic_target_regions.csv', index=False)


def report_problematic_users(df):
    report = df[
        (df['region'] == 'Bishkek') &
        (df['tariff_plan'] == 'Standard') &
        (df['over_limit'] == True)
        ][['user_id', 'traffic_gb_used', 'month']]
    print("\n--- Report 3: Problematic Users ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/problematic_users.csv', index=False)


def report_summary_by_tariff(df):
    report = df.groupby('tariff_plan').agg(
        total_traffic=('traffic_gb_used', 'sum'),
        avg_traffic=('traffic_gb_used', 'mean'),
        unique_users=('user_id', 'nunique')
    ).reset_index()
    print("\n--- Report 4: Summary by Tariff ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/summary_by_tariff.csv', index=False)


def report_top_regions(df):
    report = df.groupby('region')['traffic_gb_used'].mean().sort_values(ascending=False).head(5).reset_index()
    report = report.rename(columns={'traffic_gb_used': 'avg_traffic_gb_used'})
    print("\n--- Report 5: Top 5 Regions by Avg Traffic ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/top_regions.csv', index=False)

    # Graph
    ensure_dir('images')
    plt.figure()
    plt.bar(report['region'], report['avg_traffic_gb_used'])
    plt.title("Top 5 Regions by Average Traffic")
    plt.ylabel("Average Traffic (GB)")
    plt.savefig("images/top_regions.png")
    plt.close()


def report_traffic_extremes(df):
    report = df.groupby('tariff_plan').agg(
        min_traffic=('traffic_gb_used', 'min'),
        max_traffic=('traffic_gb_used', 'max')
    ).reset_index()
    print("\n--- Report 6: Traffic Extremes ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/traffic_extremes.csv', index=False)


def report_overlimit_analysis(df):
    df_filtered = df[df['tariff_plan'] != 'Unlimited'].copy()
    report = df_filtered.groupby('tariff_plan').agg(
        total_users=('user_id', 'nunique'),
        overlimit_users=('over_limit', 'sum')
    ).reset_index()
    report['percent_overlimit'] = (report['overlimit_users'] / report['total_users']) * 100
    print("\n--- Report 7: Overlimit Analysis ---\n")
    print(report.to_string(index=False))
    report.to_csv('reports/overlimit_analysis.csv', index=False)


def report_monthly_traffic(df):
    report = pd.pivot_table(
        df,
        index='tariff_plan',
        columns='month',
        values='traffic_gb_used',
        aggfunc='sum',
        fill_value=0
    )
    print("\n--- Report 8: Monthly Traffic ---\n")
    print(report)
    report.to_csv('reports/monthly_traffic.csv')


# ----------------------------
# MAIN
# ----------------------------

def main():
    ensure_dir('reports')
    ensure_dir('images')
    df = load_and_clean('/Users/annoyingfreak/Documents/Code/internet_traffic_jan_feb_mar.csv')

    # Run all reports
    report_subscribers_by_region(df)
    report_avg_traffic_target_regions(df)
    report_problematic_users(df)
    report_summary_by_tariff(df)
    report_top_regions(df)
    report_traffic_extremes(df)
    report_overlimit_analysis(df)
    report_monthly_traffic(df)


if __name__ == "__main__":
    main()












