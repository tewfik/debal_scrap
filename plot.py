import sys

import matplotlib.pyplot as plt
import pandas as pd


def plot(filename):
    df = pd.read_csv(filename)
    df.created_at = pd.to_datetime(df.created_at)
    df = df.set_index("created_at")

    # we are looking at expenses here, so we ignore "paiement en liquide"
    # that's what `[df.category != "hidden-xs"]` is forq
    df = df[df.category != "hidden-xs"]
    yearly_stacked_by_payer =  df.groupby([df.index.year, 'paid_by']).amount.sum().unstack(fill_value=0).plot.bar(stacked=True)
    monthly_stacked_by_payer = df.groupby([df.index.year, df.index.month, 'paid_by']).amount.sum().unstack(fill_value=0).plot.bar(stacked=True)
    monthly_stacked_by_payer = df.groupby([df.index.year, df.index.month, 'category']).amount.sum().unstack(fill_value=0).plot.bar(stacked=True)

    plt.show()


if __name__ == '__main__':
    plot(sys.argv[1])
