---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Viewing Historical Weather Data

```{code-cell} ipython3
import pandas as pd

df = (
    pd.read_parquet('../data/weather.parquet')
    .assign(
        year=lambda d: d['date'].dt.year,
        month=lambda d: d['date'].dt.month,
        day=lambda d: d['date'].dt.day,
    )
)

df.head()
```

```{code-cell} ipython3
df.dtypes
```

```{code-cell} ipython3
import matplotlib.pyplot as plt

plt.rc('font', size=14)
```

```{code-cell} ipython3
#| label: raw-viz

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 6))
ax.scatter(df['date'], df['avg_temp'], s=1, color='gray')

smooth = df.set_index('date').rolling('365D')['avg_temp'].mean()
ax.plot(smooth.index, smooth)
ax.margins(y=0, x=0)
ax.set_ylabel('temperature')
ax.set_xlabel('year');
```

## Daily Year Over Year

```{code-cell} ipython3
#| label: daily-yoy

daily_yoy = (
    df.assign(day_of_year=lambda d: d['date'].dt.day_of_year)
    .pivot(index='year', columns='day_of_year', values='avg_temp')
)

fig, ax = plt.subplots(figsize=(14, 6))
# x0 x1, y0 y1
ax.imshow(
    daily_yoy,
    extent=[daily_yoy.columns[0], daily_yoy.columns[-1], daily_yoy.index[0], daily_yoy.index[-1]]
)

ax.set(ylabel='year', xlabel='day of year')
```

## Primary viz

```{code-cell} ipython3
reference_years = (1950, 1990)
selected_year = 2024
```

```{code-cell} ipython3
ref_df = (
    df.loc[lambda d: d['date'].dt.year.between(*reference_years)]
    .groupby(['month', 'day'])
    .agg(
        lb=('avg_temp', lambda g: g.quantile(.05)),
        ub=('avg_temp', lambda g: g.quantile(.95)),
        avg=('avg_temp', 'mean'),
    )
)
ref_df.head()
```

```{code-cell} ipython3
plot_df = (
    df.loc[lambda d: d['year'] == selected_year]
    .merge(ref_df.add_prefix('ref_'), left_on=['month', 'day'], right_index=True)
    .assign(
        distance=lambda d: (d['avg_temp'] - d['ref_avg']).pipe(lambda s: s / s.abs().max())
    )
)

plot_df.head()
```

```{code-cell} ipython3
#| label: main-fig

fig, ax = plt.subplots(figsize=(14, 10))

ax.plot('date', 'ref_lb', color='k', data=plot_df, zorder=6, lw=.6, ls='--')
ax.plot('date', 'ref_ub', color='k', data=plot_df, zorder=6, lw=.6, ls='--')
ax.fill_between('date', 'ref_lb', 'ref_ub', color='gainsboro', data=plot_df, zorder=5, ec='none')
ax.plot('date', 'ref_avg', color='k', zorder=6, data=plot_df)

raw_pc = ax.fill_between(
    'date', 'avg_temp', 'ref_avg', data=plot_df, color=ax.get_facecolor(), zorder=5, lw=.5, fc='none'
)

arr = raw_pc.get_paths()[0].vertices
(x0, y0), (x1, y1) = arr.min(axis=0), arr.max(axis=0)

gradient = ax.imshow(
    plot_df[['distance']].T,
    extent=[x0, x1, y0, y1],
    cmap='RdBu_r',
    zorder=5,
)

gradient.set_clip_path(raw_pc.get_paths()[0], transform=ax.transData)
ax.use_sticky_edges = False
ax.margins(x=0, y=.01)
```

```{code-cell} ipython3

```
