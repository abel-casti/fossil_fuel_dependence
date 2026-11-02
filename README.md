# ⚡ European Fossil Dependence

**How much of each country's electricity demand could be covered by its own non-fossil generation alone?**

An end-to-end data engineering and analytics project covering **Spain, France, Belgium, Germany/Luxembourg and Poland**. It pulls hourly generation and load data from the ENTSO-E Transparency Platform (2019 → today), models it with dbt on PostgreSQL, and serves it through an interactive Power BI report.

![Dashboard overview](images/dashboard_yearly.png)

> 📚 **[Browse the dbt documentation & lineage](https://placeholder_for_dbt_documentation)**

---

## What the data says

A few things that jump out of the dashboard (2019 – 2026 year to date):

- 🇫🇷 **France is the outlier.** Its nuclear fleet plus renewables cover roughly 100%+ of its own load in most years, reaching ~116% in 2025.
- 🇵🇱 **Poland is the most fossil-dependent** of the five, but non-fossil coverage has climbed steadily from ~11% (2019) to ~32% (2026 YTD).
- 🇪🇸 **Spain has made the biggest sustained gain**, from ~61% to ~84%, thanks to a fast increase in renewable generation.
- 🇩🇪 **Germany/Luxembourg has been flat at ~55–60%** across the whole period.
- 🇧🇪 **Belgium drops from ~80% (2021) to ~41% (2026 YTD)**, the sharpest decline in the set. The cause is the phase-out of its nuclear fleet, whose generation is now virtually zero.
- Across all countries and years, generation splits roughly into **37% renewable, 31% nuclear, 29% fossil, 3% ambiguous**.

### How coverage is calculated

**Non-fossil load coverage = (nuclear + renewable generation) ÷ load**, per country and period. Values above 100% mean a country generates more non-fossil electricity than it consumes, so the surplus could be exported.

Generation sources are grouped into four categories: **nuclear**, **renewable**, **fossil**, and **ambiguous**. Ambiguous sources can't be clearly labeled as fossil or non-fossil, so they are shown in the report but counted in neither side of the calculation.

ENTSO-E reports some zones at 15-minute resolution. These readings are aggregated to hourly values in the intermediate layer, so every country shares the same grain.

Because the report goes all the way down to hourly resolution, you can also see *when* a country leans on fossil fuels: solar-driven midday peaks, overnight dips, and weekday vs. weekend patterns.

---