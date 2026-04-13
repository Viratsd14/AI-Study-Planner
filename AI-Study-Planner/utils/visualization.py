import matplotlib.pyplot as plt


def create_study_chart(names, hours):
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, hours, color='skyblue', edgecolor='navy')
    ax.set_xlabel('Subjects')
    ax.set_ylabel('Study Hours')
    ax.set_title('Study Hours Distribution')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig


def create_weekly_chart(daily_hours):
    fig, ax = plt.subplots(figsize=(10, 4))

    # Sort by date
    sorted_days = sorted(daily_hours.keys())
    hours = [daily_hours[day] for day in sorted_days]

    # Format dates nicely
    display_days = [day[5:] for day in sorted_days]  # Remove year

    colors = ['green' if h > 0 else 'lightgray' for h in hours]
    bars = ax.bar(display_days, hours, color=colors, alpha=0.7, edgecolor='black')

    ax.set_xlabel('Date')
    ax.set_ylabel('Hours Studied')
    ax.set_title('Last 7 Days Study Progress')

    # Add value labels on bars
    for bar, h in zip(bars, hours):
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    f'{h:.1f}', ha='center', va='bottom', fontsize=9)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig