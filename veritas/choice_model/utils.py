import numpy as np
import pandas as pd

from pathlib import Path


class ChoiceModel():

    def __init__(self):
        self.site_and_location = pd.read_parquet(Path().resolve() / 'choice_model/data/site_and_location.parquet')
        self.site_data = pd.read_parquet(Path().resolve() / 'choice_model/data/site_data.parquet')
        self.site_coefficients = pd.read_parquet(Path().resolve() / 'choice_model/data/site_coefficients.parquet')
        self.distances = pd.read_parquet(Path().resolve() / 'choice_model/data/distances.parquet')
        self.calibration = pd.read_parquet(Path().resolve() / 'choice_model/data/calibration.parquet')
        self.population = pd.read_parquet(Path().resolve() / 'choice_model/data/model_population.parquet')

    def _add_to_distances(self, site_name):
        self.distances.loc[site_name] = 0

    def _add_to_calibration(self, site_name):
        self.calibration.loc[site_name] = 0

    def _get_updated_site_df(self, modified_sites):
        """
        Return site data DataFrame except sites are replaced if modified versions of them exist
        :param modified_sites: list of modified site objects
        :return: DataFrame of site data with existing modified sites replaced
        """
        updated_site_data = self.site_data
        for modified_site in modified_sites:
            # dealing with a custom added site by user
            if modified_site.name not in updated_site_data.index:
                # add the new site to the data files (currently setting the values equal to 0)
                self._add_to_distances(modified_site.name)
                self._add_to_calibration(modified_site.name)
            else:
                updated_site_data = updated_site_data.drop(index=modified_site.name)
            modified_site_df = pd.DataFrame({
                'name': [modified_site.name],
                'acres': [modified_site.acres],
                'trails': [modified_site.trails], 'trail_miles': [modified_site.trail_miles],
                'picnic_area': [modified_site.picnic_area],
                'sports_facilities': [modified_site.sports_facilities],
                'swimming_facilities': [modified_site.swimming_facilities],
                'boat_launch': [modified_site.boat_launch], 'waterbody': [modified_site.waterbody],
                'bathrooms': [modified_site.bathrooms], 'playgrounds': [modified_site.playgrounds]
            })
            modified_site_df = modified_site_df.set_index('name')
            updated_site_data = pd.concat([updated_site_data, modified_site_df])
        updated_site_data = updated_site_data.astype(float)
        return updated_site_data

    def _update_model_values(self, updated_site_data):
        """
        Update the model variables based on updated sites
        """
        # add acreage_scalar
        updated_site_data['acreage_scalar'] = updated_site_data['acres']
        updated_site_data['acres'] = updated_site_data['acres']
        updated_site_data['acreage_scalar'].where(updated_site_data['acreage_scalar'] > 3000, 1, inplace=True)
        updated_site_data['acreage_scalar'].where(updated_site_data['acreage_scalar'] < 3000, 0.2, inplace=True)

        # update acres by multiplying old acres with either the 0.2 or 1
        updated_site_data['acres'] = updated_site_data['acres'].multiply(updated_site_data['acreage_scalar'])
        updated_site_data = updated_site_data.fillna(0)

        # calculate site_product from site_data and site_coefficients
        site_product = updated_site_data.iloc[:, :-1].mul(self.site_coefficients.values, axis=1).sum(axis=1)
        site_product = site_product.to_frame().rename(columns={0: "Product"})

        # calculate distance_product from distance_coefficient and distances data
        distance_coefficient = np.repeat(-0.011, self.distances.shape[1])
        distance_product = self.distances.mul(distance_coefficient, axis=1)

        # in both distance product and site product, used to add together
        ds_in_both = distance_product.index.intersection(site_product.index)

        # sort each so that they have matching index order
        site_product = site_product.sort_index()
        distance_product = distance_product.loc[ds_in_both].sort_index()

        self.site_attractiveness = distance_product.add(site_product.values, axis=1)

        self.exp_site_attractiveness = np.exp(self.site_attractiveness)

        ec_in_both = self.exp_site_attractiveness.index.intersection(self.calibration.index)
        new_calibration = self.calibration.loc[ec_in_both]

        calibrated_attractiveness = self.exp_site_attractiveness.add(new_calibration.values, axis=1)

        self.visitation_probability = calibrated_attractiveness.div(calibrated_attractiveness.sum(axis=0), axis=1)
        self.visitation_probability[self.visitation_probability < 0] = 0


    def get_site_choice_visit_prob(self, modified_sites):
        """
        Returns dictionary with sites and their respective visit probability
        """
        # replace old site_data with modified sites
        modified_site_data = self._get_updated_site_df(modified_sites)

        # update model values
        self._update_model_values(modified_site_data)

        # convert the average visitation probabilites into dictionary
        average_visitation_prob = self.visitation_probability.mean(axis=1)
        site_choice_probs = {}
        for name, prob in zip(average_visitation_prob.index.to_list(), average_visitation_prob.values.tolist()):
            site_choice_probs[name] = prob

        return site_choice_probs

    def get_equity_evaluation(self, modified_sites):
        """
        Returns dictionary the equity evaluations
        """
        # replace old site_data with modified sites
        modified_site_data = self._get_updated_site_df(modified_sites)

        # update model values
        self._update_model_values(modified_site_data)

        site_attractiveness = self.site_attractiveness
        site_attractiveness[site_attractiveness == 0] = -1000
        utility_index = np.log(self.exp_site_attractiveness)
        
        # Underserved Evaluation
        percent_black = self.population['Black'] / (self.population['Black'] + self.population['Other'])
        percent_other = self.population['Other'] / (self.population['Black'] + self.population['Other'])

        underserved_evaluation_black = percent_black / (self.visitation_probability * utility_index).sum(axis=0)
        underserved_evaluation_other = percent_other / (self.visitation_probability * utility_index).sum(axis=0)

        # Population Trips
        trips_per_person = 10 * 15.79 / 11.29
        population_trips = self.population * trips_per_person

        # Total Trips by Equity Group
        total_trips_by_equity_group = population_trips.sum()

        # All Trips
        all_trips_black = population_trips['Black'] * self.visitation_probability
        all_trips_other = population_trips['Other'] * self.visitation_probability
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
        return equity_evaluation

    def get_visitation_probability(self, modified_sites):
        # replace old site_data with modified sites
        modified_site_data = self._get_updated_site_df(modified_sites)

        # update model values
        self._update_model_values(modified_site_data)

        return self.visitation_probability
