import pandas as pd
import matplotlib.pyplot as plt


def show(dates, dollars):
  df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Dollars": dollars
  })

  plt.figure(figsize=(10, 5))
  plt.plot(df["Date"], df["Dollars"], marker="o", linewidth=2)

  plt.xlabel("Date")
  plt.ylabel("Dollars ($)")
  plt.title("Value Over Time")
  plt.grid(True)

  plt.tight_layout()
  plt.show()
