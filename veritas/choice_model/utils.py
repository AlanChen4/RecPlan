import numpy as np
import pandas as pd

from pathlib import Path


def get_site_choice_prob(sites, underserved_evaluation=True):
    """
    Calculates the average site choice probability based on exponential total utility
    :param sites: list of modified sites
    :param underserved_evaluation: if True, returns the evaluation of equity groups as well
    :return: 2D array representing site choice probabilities
    """
    site_data = pd.read_parquet(Path().resolve() / 'choice_model/data/site_data.parquet')
    site_coefficients = pd.read_parquet(Path().resolve() / 'choice_model/data/site_coefficients.parquet')
    distances = pd.read_parquet(Path().resolve() / 'choice_model/data/distances.parquet')
    calibration = pd.read_parquet(Path().resolve() / 'choice_model/data/calibration.parquet')
    population = pd.read_parquet(Path().resolve() / 'choice_model/data/model_population.parquet')

    # replace old site_data with modified sites
    for site in sites:
        site_data = site_data.drop(index=site.name)
        modified_site = pd.DataFrame({
            'name': [site.name],
            'acres': [site.acres],
            'trails': [site.trails], 'trail_miles': [site.trail_miles],
            'picnic_area': [site.picnic_area],
            'sports_facilities': [site.sports_facilities],
            'swimming_facilities': [site.swimming_facilities],
            'boat_launch': [site.boat_launch], 'waterbody': [site.waterbody],
            'bathrooms': [site.bathrooms], 'playgrounds': [site.playgrounds]
        })
        modified_site = modified_site.set_index('name')
        site_data = site_data.append(modified_site)
    site_data = site_data.astype(float)

    # add acreage_scalar
    site_data['acreage_scalar'] = site_data['acres']
    site_data['acres'] = site_data['acres']
    site_data['acreage_scalar'].where(site_data['acreage_scalar'] > 3000,
                                      1, inplace=True)
    site_data['acreage_scalar'].where(site_data['acreage_scalar'] < 3000,
                                      0.2, inplace=True)

    # update acres by multiplying old acres with either the 0.2 or 1
    site_data['acres'] = site_data['acres'].multiply(site_data['acreage_scalar'])
    site_data = site_data.fillna(0)

    # calculate site_product from site_data and site_coefficients
    site_product = site_data.iloc[:, :-1].mul(site_coefficients.values,
                                              axis=1).sum(axis=1)
    site_product = site_product.to_frame().rename(columns={0: "Product"})

    # calculate distance_product from distance_coefficient and distances data
    distance_coefficient = np.repeat(-0.011, distances.shape[1])
    distance_product = distances.mul(distance_coefficient, axis=1)

    # in both distance product and site product, used to add together
    ds_in_both = distance_product.index.intersection(site_product.index)

    # sort each so that they have matching index order
    site_product = site_product.sort_index()
    distance_product = distance_product.loc[ds_in_both].sort_index()

    site_attractiveness = distance_product.add(site_product.values,
                                               axis=1)

    exp_site_attractiveness = np.exp(site_attractiveness)

    ec_in_both = exp_site_attractiveness.index.intersection(calibration.index)
    calibration = calibration.loc[ec_in_both]

    calibrated_attractiveness = exp_site_attractiveness.add(calibration.values, axis=1)

    visitation_probability = calibrated_attractiveness.div(calibrated_attractiveness.sum(axis=0), axis=1)
    visitation_probability[visitation_probability < 0] = 0

    average_visitation_probability = visitation_probability.mean(axis=1)

    output = [[i, s] for i, s in zip(average_visitation_probability.index.to_list(),
                                     average_visitation_probability.values.tolist())]

    # equity_evaluation not needed
    if not underserved_evaluation:
        return output

    site_attractiveness[site_attractiveness == 0] = -1000
    utility_index = np.log(exp_site_attractiveness)
    
    # Underserved Evaluation
    percent_black = population['Black'] / (population['Black'] + population['Other'])
    percent_other = population['Other'] / (population['Black'] + population['Other'])

    underserved_evaluation_black = percent_black / (visitation_probability * utility_index).sum(axis=0)
    underserved_evaluation_other = percent_other / (visitation_probability * utility_index).sum(axis=0)

    # Population Trips
    trips_per_person = 10 * 15.79 / 11.29
    population_trips = population * trips_per_person

    # Total Trips by Equity Group
    total_trips_by_equity_group = population_trips.sum()

    # All Trips
    all_trips_black = population_trips['Black'] * visitation_probability
    all_trips_other = population_trips['Other'] * visitation_probability
    all_trips_total = all_trips_black + all_trips_other

    # Utility Weighted Trips
    utility_weighted_trips_black = all_trips_black * utility_index
    utility_weighted_trips_other = all_trips_other * utility_index
    utility_weighted_trips_total = all_trips_total * utility_index

    # Total Utility by Equity Group
    total_utility_black = utility_weighted_trips_black.sum().sum()
    total_utility_other = utility_weighted_trips_other.sum().sum()

    # Average Utility by Equity Group
    average_utility_black = total_utility_black / total_trips_by_equity_group['Black']
    average_utility_other = total_utility_other / total_trips_by_equity_group['Other']

    # Exponentiate and find ratio
    exp_average_utility_black = np.exp(average_utility_black)
    exp_average_utility_other = np.exp(average_utility_other)

    exp_ratio_black = exp_average_utility_black / (exp_average_utility_black + exp_average_utility_other)
    exp_ratio_other = exp_average_utility_other / (exp_average_utility_black + exp_average_utility_other)

    equity_evaluation = {
        'average_utility_black': exp_ratio_black, 
        'average_utility_other': exp_ratio_other
    }

    return output, equity_evaluation