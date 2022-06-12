import h3
import numpy as np

from choice_model.models import *
from choice_model.constants import *
from sklearn.linear_model import LinearRegression


class ChoiceModel():

    def __init__(self, user, bundle=None):
        """
        if using bundle_id of None, all calculations will return the baseline
        """
        self.baseline_model = self._get_baseline_model(user)
        self.baseline_sites = self._get_baseline_sites()
        self.modified_sites = self._get_modified_sites(bundle)

        self.site_data = self._update_site_data()
        self.distances = self._update_distances()

    def _get_baseline_model(self, user):
        """
        check if there are any recalibrated baseline models belonging to the user. if there are, return the one that is being used (using the selected attribute)
        """
        if BaselineModel.objects.filter(user=user, selected=True).exists():
            return BaselineModel.objects.get(user=user, selected=True)
        return None

    def _get_baseline_sites(self):
        return BaselineSite.objects.filter(baseline_model=self.baseline_model)

    def _get_modified_sites(self, bundle):
        if bundle is not None:
            return ModifiedSite.objects.filter(bundle=bundle)
        return []

    def _update_site_data(self):
        """
        return updated site data with new sites added into dataframe and ones with changed values updated accordingly
        """
        updated_site_data = SITE_DATA.copy()
        for modified_site in self.modified_sites:

            # either update row if site already exists or add row for new sites
            modified_site_name = modified_site.name
            modified_site_attributes = [
                modified_site.acres, 
                modified_site.trails, 
                modified_site.trail_miles, 
                modified_site.picnic_area, 
                modified_site.sports_facilities,
                modified_site.swimming_facilities,
                modified_site.boat_launch,
                modified_site.waterbody,
                modified_site.bathrooms,
                modified_site.playgrounds,
            ]
            updated_site_data.loc[modified_site_name] = modified_site_attributes 

        return updated_site_data

    def _update_distances(self):
        """
        for any sites that are added by the user, the distances matrix will have to add a new row with the new distances
        """
        updated_distances = DISTANCES.copy()
        for modified_site in self.modified_sites:
            modified_site_name = modified_site.name

            # ensure that only custom added sites are being added
            if modified_site_name not in SITE_DATA.index:
                new_distances = []
                for block_group in DISTANCES.columns:
                    block_group_lat, block_group_lon = float(block_group.split(', ')[-2]), float(block_group.split(', ')[-1])
                    modified_site_lat, modified_site_lon = modified_site.latitude, modified_site.longitude
                    
                    # calculate distance between the two points first in meters, and then convert to mile(s)
                    distance = h3.point_dist((block_group_lat, block_group_lon), (modified_site_lat, modified_site_lon))
                    distance *= 0.000621371

                    new_distances.append(distance)

                # add the row of new distances
                updated_distances.loc[modified_site_name] = new_distances

        return updated_distances

    def _get_site_attractiveness(self):
        """
        return attractiveness of each site (combination of site characteristics + distance + ...)
        """
        # update acres using a scalar
        acreage_scalar = self.site_data['acres'].where(self.site_data['acres'] >= 3000, 1)
        acreage_scalar = acreage_scalar.where(self.site_data['acres'] < 3000, 0.2)
        self.site_data['acres'] = self.site_data['acres'].multiply(acreage_scalar)

        # calculate site_product from site_data and site_coefficients
        site_product = self.site_data.mul(SITE_COEFFICIENTS.values, axis=1).sum(axis=1)
        site_product = site_product.to_frame().rename(columns={0: "Product"})

        # calculate distance_product from distance_coefficient and distances data
        distance_coefficient = np.repeat(-0.011, DISTANCES.shape[1])
        distance_product = self.distances.mul(distance_coefficient, axis=1)

        # in both distance product and site product, used to add together
        ds_in_both = distance_product.index.intersection(site_product.index)

        # sort each so that they have matching index order
        site_product = site_product.sort_index()
        distance_product = distance_product.loc[ds_in_both].sort_index()

        site_attractiveness = distance_product.add(site_product.values, axis=1)

        # calibrate site_attractiveness using baseline true visits data and predicted SA
        true_visits = []
        pred_site_attractiveness = []

        # use pre-saved baseline data if user does not add baseline model, otherwise use true trips according to selected baseline
        new_baseline_sites = {site.name: site.visits for site in BaselineSite.objects.filter(baseline_model=self.baseline_model)}
        for site in site_attractiveness.index:

            # occurs when dealing with custom added site
            if site not in BASELINE_VISITS.index:
                true_visits.append(0)
            else:
                if self.baseline_model is None:
                    true_visits.append(BASELINE_VISITS.loc[site].visits)
                else:
                    true_visits.append(new_baseline_sites[site].visits)

            # deals with error since there are duplicated of sites in initial data
            sa = site_attractiveness.loc[site].sum()
            if isinstance(sa, float):
                pred_site_attractiveness.append(sa)
            else:
                pred_site_attractiveness.append(sa.values[0])

        # calculate calibration value
        true_trips = np.array(true_visits).reshape((-1, 1))
        pred_SA = np.array(pred_site_attractiveness).reshape((-1, 1))
        model = LinearRegression().fit(true_trips, pred_SA)
        B0 = model.intercept_
        B1 = model.coef_
        true_SA = (true_trips - B0)/B1
        SA_adjuster = true_SA - pred_SA

        exp_site_attractiveness = np.exp(site_attractiveness)
        calibrated_attractiveness = exp_site_attractiveness.add(SA_adjuster, axis=1)
            
        return calibrated_attractiveness

    def get_site_visitation_probability(self):
        site_attractiveness = self._get_site_attractiveness()

        visitation_probability = site_attractiveness.div(site_attractiveness.sum(axis=0), axis=1)
        visitation_probability[visitation_probability < 0] = 0

        # check edge case where one site has SA of infinity
        if np.isinf(site_attractiveness).values.sum() > 0:
            visitation_probability = visitation_probability.fillna(1.0)

        return visitation_probability

    def get_site_visits(self):
        """
        return dictionary with site names as keys and their respective visits from population as values
        """
        # use visitation probabilities along with population numbers to find number of people
        visitation_probability = self.get_site_visitation_probability()
        visits = visitation_probability.multiply(POPULATION.sum(axis=1)).sum(axis=1).to_frame().rename(columns={0: 'visits'})

        return visits

    def get_site_locations(self):
        """
        return dataframe with index as site name, columns as the lat & lon
        """
        site_locations = SITE_LOCATIONS.copy()
        for modified_site in self.modified_sites:

            # only have to deal with custom added sites
            if modified_site.name not in site_locations.index:
                site_locations.loc[modified_site.name] = [modified_site.latitude, modified_site.longitude]

        return site_locations

    def get_equity_evaluation(self):
        """
        return equity evaluations for black and non-black groups
        """
        exp_site_attractiveness = self._get_site_attractiveness()
        exp_site_attractiveness[exp_site_attractiveness <= 0] = 1
        utility_index = np.log(exp_site_attractiveness)

        visitation_probability = self.get_site_visitation_probability()

        all_trips_black = POPULATION['Black'] * visitation_probability
        all_trips_other = POPULATION['Other'] * visitation_probability

        total_utility_black = (all_trips_black * utility_index).sum().sum()
        total_utility_other = (all_trips_other * utility_index).sum().sum()

        # Total Trips by Equity Group
        total_trips_by_equity_group = POPULATION.sum()

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

    def get_utility_by_block_group(self):
        exp_site_attractiveness = self._get_site_attractiveness()
        exp_site_attractiveness[exp_site_attractiveness <= 0] = 1
        utility_index = np.log(exp_site_attractiveness)

        visitation_probability = self.get_site_visitation_probability()

        all_trips_black = POPULATION['Black'] * visitation_probability
        all_trips_other = POPULATION['Other'] * visitation_probability

        utility_weighted_trips_black = all_trips_black * utility_index
        utility_weighted_trips_other = all_trips_other * utility_index

        return utility_weighted_trips_black, utility_weighted_trips_other       
