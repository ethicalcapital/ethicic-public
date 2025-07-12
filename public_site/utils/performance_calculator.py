"""
Performance calculation utilities for strategy pages.
Handles compound return calculations from monthly data.
"""
from datetime import UTC, date, datetime


def parse_percentage(value: str) -> float:
    """Convert percentage string like '2.74%' to float 0.0274"""
    if not value or value == "N/A":
        return 0.0
    try:
        # Clean the value - remove % and any trailing characters
        clean_value = value.strip().replace("%", "").replace('"', "").replace(",", ".")
        return float(clean_value) / 100
    except (ValueError, AttributeError):
        # If we can't parse it, return 0
        return 0.0


def format_percentage(value: float) -> str:
    """Convert float 0.0274 to string '2.74%'"""
    return f"{value * 100:.2f}%"


def compound_returns(returns: list[float]) -> float:
    """
    Calculate compound return from a list of periodic returns.
    returns: List of returns as decimals (e.g., 0.0274 for 2.74%)
    """
    if not returns:
        return 0.0

    compound = 1.0
    for r in returns:
        compound *= 1 + r

    return compound - 1


def calculate_ytd_return(
    monthly_returns: dict[str, dict[str, str]], current_year: int
) -> tuple[float, float]:
    """
    Calculate YTD return from monthly returns data.
    Returns tuple of (strategy_return, benchmark_return)
    """
    year_str = str(current_year)
    if year_str not in monthly_returns:
        return 0.0, 0.0

    year_data = monthly_returns[year_str]
    strategy_returns = []
    benchmark_returns = []

    # Month order
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    for month in months:
        if month in year_data:
            strategy = year_data[month].get("strategy", "")
            benchmark = year_data[month].get("benchmark", "")

            if strategy and strategy != "N/A":
                strategy_returns.append(parse_percentage(strategy))
            else:
                # If no data for this month, stop (we've reached current month)
                break

            if benchmark and benchmark != "N/A":
                benchmark_returns.append(parse_percentage(benchmark))

    return compound_returns(strategy_returns), compound_returns(benchmark_returns)


def calculate_one_year_return(
    monthly_returns: dict[str, dict[str, str]], current_date: date
) -> tuple[float, float]:
    """
    Calculate trailing 12-month return.
    Returns tuple of (strategy_return, benchmark_return)
    """
    strategy_returns = []
    benchmark_returns = []

    # Get last 12 months of data
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    current_month_idx = current_date.month - 1
    current_year = current_date.year

    # Collect 12 months of data going backwards
    for i in range(12):
        month_idx = (current_month_idx - i) % 12
        year = current_year if (current_month_idx - i) >= 0 else current_year - 1

        year_str = str(year)
        month = months[month_idx]

        if year_str in monthly_returns and month in monthly_returns[year_str]:
            month_data = monthly_returns[year_str][month]
            strategy = month_data.get("strategy", "")
            benchmark = month_data.get("benchmark", "")

            if strategy and strategy != "N/A":
                strategy_returns.append(parse_percentage(strategy))
            if benchmark and benchmark != "N/A":
                benchmark_returns.append(parse_percentage(benchmark))

    # Reverse to get chronological order
    strategy_returns.reverse()
    benchmark_returns.reverse()

    return compound_returns(strategy_returns), compound_returns(benchmark_returns)


def calculate_three_year_return(
    monthly_returns: dict[str, dict[str, str]],
    current_date: date,
    inception_date: date = None,
) -> tuple[float, float]:
    """
    Calculate trailing 3-year annualized return.
    Returns tuple of (strategy_return, benchmark_return)
    """
    strategy_returns = []
    benchmark_returns = []

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    # Find the last month with data
    last_data_year = max(int(y) for y in monthly_returns)
    last_data_month_idx = -1

    for i in range(11, -1, -1):  # Check from Dec to Jan
        if months[i] in monthly_returns.get(str(last_data_year), {}):
            last_data_month_idx = i
            break

    if last_data_month_idx == -1:  # No data in the last year
        return None, None

    # Use the last data month instead of current date if current date is beyond data
    last_data_date = date(last_data_year, last_data_month_idx + 1, 1)
    if last_data_date < current_date:
        current_month_idx = last_data_month_idx
        current_year = last_data_year
    else:
        current_month_idx = current_date.month - 1
        current_year = current_date.year

    # Collect 36 months of data going backwards
    for i in range(36):
        # Calculate how many months back we're going
        months_back = i

        # Calculate year and month
        year = current_year - (months_back + (11 - current_month_idx)) // 12
        month_idx = (current_month_idx - months_back) % 12

        if month_idx < 0:
            month_idx += 12

        year_str = str(year)
        month = months[month_idx]

        if year_str in monthly_returns and month in monthly_returns[year_str]:
            month_data = monthly_returns[year_str][month]
            strategy = month_data.get("strategy", "")
            benchmark = month_data.get("benchmark", "")

            if strategy and strategy != "N/A":
                strategy_returns.append(parse_percentage(strategy))
            if benchmark and benchmark != "N/A":
                benchmark_returns.append(parse_percentage(benchmark))

    # Reverse to get chronological order
    strategy_returns.reverse()
    benchmark_returns.reverse()

    # Check if we have enough data for three years
    # If inception date is provided, check if strategy has been operative for 3 years
    if inception_date:
        years_since_inception = (current_date - inception_date).days / 365.25
        if years_since_inception < 3:
            # Return None to indicate not enough data
            return None, None

    # For strategies operative for 3+ years, require at least 30 months of data (allowing for some gaps)
    # For newer strategies, we'll already have returned None above
    if len(strategy_returns) < 30:
        return None, None

    # Calculate compound returns
    strategy_compound = compound_returns(strategy_returns)
    benchmark_compound = compound_returns(benchmark_returns)

    # Annualize (if we have full 3 years of data)
    if len(strategy_returns) >= 36:
        strategy_annualized = (1 + strategy_compound) ** (1 / 3) - 1
    else:
        # If less than 3 years, annualize based on actual months
        years = len(strategy_returns) / 12
        strategy_annualized = (
            (1 + strategy_compound) ** (1 / years) - 1 if years > 0 else 0
        )

    if len(benchmark_returns) >= 36:
        benchmark_annualized = (1 + benchmark_compound) ** (1 / 3) - 1
    else:
        years = len(benchmark_returns) / 12
        benchmark_annualized = (
            (1 + benchmark_compound) ** (1 / years) - 1 if years > 0 else 0
        )

    return strategy_annualized, benchmark_annualized


def _extract_returns_since_inception(
    monthly_returns: dict[str, dict[str, str]], inception_date: date, current_date: date
) -> tuple[list[float], list[float]]:
    """Extract strategy and benchmark returns since inception date."""
    strategy_returns = []
    benchmark_returns = []

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    for year in sorted(monthly_returns.keys()):
        year_int = int(year)

        for month_idx, month in enumerate(months):
            month_date = date(year_int, month_idx + 1, 1)

            if month_date < inception_date:
                continue
            if month_date > current_date:
                break

            if month in monthly_returns[year]:
                month_data = monthly_returns[year][month]
                strategy = month_data.get("strategy", "")
                benchmark = month_data.get("benchmark", "")

                if strategy and strategy != "N/A":
                    strategy_returns.append(parse_percentage(strategy))
                if benchmark and benchmark != "N/A":
                    benchmark_returns.append(parse_percentage(benchmark))

    return strategy_returns, benchmark_returns


def _annualize_returns(returns: list[float], compound_return: float) -> float:
    """Annualize returns based on actual time period."""
    if not returns:
        return 0.0

    months_count = len(returns)
    years = months_count / 12

    if years > 1:
        return (1 + compound_return) ** (1 / years) - 1
    return compound_return


def calculate_since_inception_return(
    monthly_returns: dict[str, dict[str, str]], inception_date: date, current_date: date
) -> tuple[float, float]:
    """
    Calculate annualized return since inception.
    Returns tuple of (strategy_return, benchmark_return)
    """
    strategy_returns, benchmark_returns = _extract_returns_since_inception(
        monthly_returns, inception_date, current_date
    )

    # Calculate compound returns
    strategy_compound = compound_returns(strategy_returns)
    benchmark_compound = compound_returns(benchmark_returns)

    # Annualize based on actual time period
    strategy_annualized = _annualize_returns(strategy_returns, strategy_compound)
    benchmark_annualized = _annualize_returns(benchmark_returns, benchmark_compound)

    return strategy_annualized, benchmark_annualized


def update_performance_from_monthly_data(
    strategy_page, monthly_returns: dict[str, dict[str, str]]
):
    """
    Update all performance fields on a StrategyPage based on monthly returns data.

    monthly_returns format:
    {
        "2024": {
            "Jan": {"strategy": "2.74%", "benchmark": "3.28%"},
            "Feb": {"strategy": "2.49%", "benchmark": "-0.35%"},
            ...
        },
        "2025": {...}
    }
    """
    current_date = datetime.now(UTC).date()
    current_year = current_date.year

    # Calculate YTD
    ytd_strategy, ytd_benchmark = calculate_ytd_return(monthly_returns, current_year)
    strategy_page.ytd_return = format_percentage(ytd_strategy)
    strategy_page.ytd_benchmark = format_percentage(ytd_benchmark)
    strategy_page.ytd_difference = format_percentage(ytd_strategy - ytd_benchmark)

    # Calculate 1-year
    one_yr_strategy, one_yr_benchmark = calculate_one_year_return(
        monthly_returns, current_date
    )
    strategy_page.one_year_return = format_percentage(one_yr_strategy)
    strategy_page.one_year_benchmark = format_percentage(one_yr_benchmark)
    strategy_page.one_year_difference = format_percentage(
        one_yr_strategy - one_yr_benchmark
    )

    # Calculate 3-year
    three_yr_strategy, three_yr_benchmark = calculate_three_year_return(
        monthly_returns, current_date, strategy_page.inception_date
    )

    # If None is returned, the strategy hasn't been operative for 3 years
    if three_yr_strategy is None or three_yr_benchmark is None:
        strategy_page.three_year_return = "-"
        strategy_page.three_year_benchmark = "-"
        strategy_page.three_year_difference = "-"
    else:
        strategy_page.three_year_return = format_percentage(three_yr_strategy)
        strategy_page.three_year_benchmark = format_percentage(three_yr_benchmark)
        strategy_page.three_year_difference = format_percentage(
            three_yr_strategy - three_yr_benchmark
        )

    # Calculate since inception
    if strategy_page.inception_date:
        si_strategy, si_benchmark = calculate_since_inception_return(
            monthly_returns, strategy_page.inception_date, current_date
        )
        strategy_page.since_inception_return = format_percentage(si_strategy)
        strategy_page.since_inception_benchmark = format_percentage(si_benchmark)
        strategy_page.since_inception_difference = format_percentage(
            si_strategy - si_benchmark
        )
