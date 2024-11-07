import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Suppress interactive plotting
plt.ioff()

# Load data
file_path_fr = "https://raw.githubusercontent.com/U1186204/interest_rate_by_assets_project/refs/heads/main/FEDFUNDS.csv"
file_path_gld = "https://raw.githubusercontent.com/U1186204/interest_rate_by_assets_project/refs/heads/main/MacroTrends_Data_Download.csv"

df_ir = pd.read_csv(file_path_fr)
df_gld = pd.read_csv(file_path_gld, skiprows=10)

# Convert date columns to datetime format
df_gld["date"] = pd.to_datetime(df_gld["date"])
df_ir["DATE"] = pd.to_datetime(df_ir["DATE"])

# Merge data on the date column
df_gld_by_ir = pd.merge(df_gld, df_ir, left_on="date", right_on="DATE", how="inner")

# Set 'date' as the index to use resample
df_gld_by_ir.set_index("date", inplace=True)

# Resample data to yearly frequency and calculate the mean for each year
df_resampled_yoy = df_gld_by_ir.resample("YE").mean().reset_index()
df_resampled_mom = (
    df_gld_by_ir.resample("ME").mean().reset_index()  # Monthly for MoM charts
)


# Define a function to create and save the plot for a given date range
def create_and_save_plot(
    data,
    start_year,
    end_year,
    title,
    filename,
    yoy_annotations=False,
    resample_type="yoy",
):
    # Select data type based on resample type
    data_filtered = data[
        (data["date"].dt.year >= start_year) & (data["date"].dt.year <= end_year)
    ]

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Set a black background color
    fig.patch.set_facecolor("black")
    ax1.set_facecolor("black")

    # Plot gold prices on the left y-axis
    ax1.plot(
        data_filtered["date"], data_filtered["real"], color="gold", label="Gold Price"
    )
    ax1.set_xlabel("Year", color="white")
    ax1.set_ylabel("Gold Price (USD)", color="gold")
    ax1.tick_params(axis="y", labelcolor="gold")

    # Set x-axis ticks
    if start_year == 1950 and end_year == 2023:
        ax1.xaxis.set_major_locator(
            mdates.YearLocator(10)
        )  # 10-year intervals for full chart
    else:
        ax1.xaxis.set_major_locator(
            mdates.YearLocator(1)
        )  # 1-year intervals for shorter charts
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.tick_params(axis="x", colors="white")

    # Add grid lines
    ax1.grid(color="gray", linestyle="--", linewidth=0.5)

    # Create a second y-axis for interest rates with white labels and lines
    ax2 = ax1.twinx()
    ax2.plot(
        data_filtered["date"],
        data_filtered["FEDFUNDS"],
        color="white",
        label="Interest Rate",
    )
    ax2.set_ylabel("Interest Rate (%)", color="white")
    ax2.tick_params(axis="y", labelcolor="white")

    # Add a legend with a white background
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    legend = ax1.legend(
        lines + lines2,
        labels + labels2,
        loc="upper left",
        fontsize=10,
        facecolor="white",  # Set the background of the legend to white
        edgecolor="white",
    )

    # Set title color to white
    plt.title(title, color="white")

    # Add year-on-year annotations for gold and month-over-month for interest rates in shorter charts if specified
    if yoy_annotations:
        yearly_data = data_filtered[data_filtered["date"].dt.is_year_start]
        for i, row in yearly_data.iterrows():
            # Annotate gold price
            ax1.annotate(
                f"{row['real']:.0f}",
                (row["date"], row["real"]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                color="gold",
                fontsize=8,
            )
            # Annotate interest rate
            ax2.annotate(
                f"{row['FEDFUNDS']:.1f}",
                (row["date"], row["FEDFUNDS"]),
                textcoords="offset points",
                xytext=(0, -10),
                ha="center",
                color="white",
                fontsize=8,
            )

    # Adjust layout and save the figure
    fig.tight_layout()
    output_path = f"images/{filename}.png"
    os.makedirs("images", exist_ok=True)  # Ensure the images folder exists
    plt.savefig(
        output_path, facecolor=fig.get_facecolor()
    )  # Save with black background
    plt.close(fig)  # Close the figure to avoid displaying it in a loop


# Create and save the four required plots
# YoY for full data
create_and_save_plot(
    df_resampled_yoy,
    1950,
    2023,
    "Gold Prices and Interest Rates Over Time",
    "gold_interest_full",
)

# MoM for the other 3-year subperiods, but show only YoY annotations
create_and_save_plot(
    df_resampled_mom,
    1970,
    1980,
    "Gold Prices and Interest Rates (1970-1980)",
    "gold_interest_1970_1980",
    yoy_annotations=True,
)
create_and_save_plot(
    df_resampled_mom,
    1980,
    1985,
    "Gold Prices and Interest Rates (1980-1985)",
    "gold_interest_1980_1985",
    yoy_annotations=True,
)
create_and_save_plot(
    df_resampled_mom,
    2008,
    2012,
    "Gold Prices and Interest Rates (2008-2012)",
    "gold_interest_2008_2012",
    yoy_annotations=True,
)
