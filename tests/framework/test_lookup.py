import numpy as np
import pandas as pd

from vivarium.test_util import build_table, setup_simulation, TestPopulation


def test_interpolated_tables(base_config):
    year_start = base_config.time.start.year
    year_end = base_config.time.end.year
    years = build_table(lambda age, sex, year: year, year_start, year_end)
    ages = build_table(lambda age, sex, year: age, year_start, year_end)
    one_d_age = ages.copy()
    del one_d_age['year']
    one_d_age = one_d_age.drop_duplicates()

    simulation = setup_simulation([TestPopulation()], 10000, input_config=base_config)
    manager = simulation.tables
    years = manager.build_table(years)
    ages = manager.build_table(ages)
    one_d_age = manager.build_table(one_d_age, parameter_columns=('age',))

    result_years = years(simulation.population.population.index)
    result_ages = ages(simulation.population.population.index)
    result_ages_1d = one_d_age(simulation.population.population.index)

    fractional_year = simulation.clock.time.year
    fractional_year += simulation.clock.time.timetuple().tm_yday / 365.25

    assert np.allclose(result_years, fractional_year)
    assert np.allclose(result_ages, simulation.population.population.age)
    assert np.allclose(result_ages_1d, simulation.population.population.age)

    simulation.clock._time += pd.Timedelta(30.5 * 125, unit='D')
    simulation.population._population.age += 125/12

    result_years = years(simulation.population.population.index)
    result_ages = ages(simulation.population.population.index)
    result_ages_1d = one_d_age(simulation.population.population.index)

    fractional_year = simulation.clock.time.year
    fractional_year += simulation.clock.time.timetuple().tm_yday / 365.25

    assert np.allclose(result_years, fractional_year)
    assert np.allclose(result_ages, simulation.population.population.age)
    assert np.allclose(result_ages_1d, simulation.population.population.age)


def test_interpolated_tables_without_uniterpolated_columns(base_config):
    year_start = base_config.time.start.year
    year_end = base_config.time.end.year
    years = build_table(lambda age, sex, year: year, year_start, year_end)
    del years['sex']
    years = years.drop_duplicates()

    simulation = setup_simulation([TestPopulation()], 10000, input_config=base_config)
    manager = simulation.tables
    years = manager.build_table(years, key_columns=(), parameter_columns=('year', 'age',))

    result_years = years(simulation.population.population.index)

    fractional_year = simulation.clock.time.year
    fractional_year += simulation.clock.time.timetuple().tm_yday / 365.25

    assert np.allclose(result_years, fractional_year)

    simulation.clock._time += pd.Timedelta(30.5 * 125, unit='D')

    result_years = years(simulation.population.population.index)

    fractional_year = simulation.clock.time.year
    fractional_year += simulation.clock.time.timetuple().tm_yday / 365.25

    assert np.allclose(result_years, fractional_year)


def test_interpolated_tables__exact_values_at_input_points(base_config):
    year_start = base_config.time.start.year
    year_end = base_config.time.end.year
    years = build_table(lambda age, sex, year: year, year_start, year_end)
    input_years = years.year.unique()

    simulation = setup_simulation([TestPopulation()], 10000, input_config=base_config)
    manager = simulation.tables
    years = manager.build_table(years)

    for year in input_years:
        simulation.clock._time = pd.Timestamp(year, 1, 1)
        assert np.allclose(years(simulation.population.population.index),
                           simulation.clock.time.year + 1/365, rtol=1.e-5)
