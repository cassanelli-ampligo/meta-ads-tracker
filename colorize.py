import pandas as pd


def colorize(campaigns):

    # Convert to DataFrame
    df = pd.DataFrame(campaigns)
    df = df.sort_values(by=["CPF"], ascending=[False])

    # Function to apply conditional coloring
    def color_cpf_values(val):

        if isinstance(val, str):
            val = float(val.replace("€", ""))

        color = "white"

        if val <= 0.25:
            color = "#98FB98"  # Light green
        elif 0.25 < val < 0.30:
            color = "#FFD700"  # Gold
        elif val > 0.30:
            color = "#FF4500"  # Darker red (Hex code)
        return f"color: {color}"

    # Applying the styling
    styled_df = df.style.applymap(color_cpf_values, subset=["CPF", "CPF - Real"])

    return styled_df
