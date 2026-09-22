import requests
import logging
import time

class HospitalService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_nearby_hospitals(self, lat, lng, radius=5000, retries=3, delay=2):
        for attempt in range(retries):
            try:
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=hospital&key={self.api_key}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                logging.info(f"Places API response: {data}")
                if data.get('status') != 'OK':
                    error_message = data.get('error_message', 'Unknown error')
                    logging.error(f"Places API error: {data.get('status')} - {error_message}")
                    return []

                results = [r for r in data.get('results', []) if r.get('business_status') == 'OPERATIONAL']
                if not results:
                    logging.warning(f"No hospitals found within {radius}m of ({lat}, {lng})")
                return results
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt+1} failed for hospital search: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logging.error(f"Error fetching nearby hospitals: {str(e)}")
                    return []

    def get_hospital_details(self, place_id, retries=3, delay=2):
        for attempt in range(retries):
            try:
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,formatted_address&key={self.api_key}"
                details_response = requests.get(details_url)
                details_response.raise_for_status()
                details_data = details_response.json()

                logging.info(f"Hospital details response for place_id {place_id}: {details_data}")
                if details_data.get('status') != 'OK':
                    error_message = details_data.get('error_message', 'Unknown error')
                    logging.error(f"Hospital details API error: {details_data.get('status')} - {error_message}")
                    return {}

                return details_data.get('result', {})
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt+1} failed for hospital details: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logging.error(f"Error fetching hospital details: {str(e)}")
                    return {}

    def fetch_hospital_details_list(self, lat, lng):
        hospitals = self.get_nearby_hospitals(lat, lng)
        hospital_details_list = []
        for hospital in hospitals:
            place_id = hospital.get('place_id')
            if place_id:
                details = self.get_hospital_details(place_id)
                if details:
                    hospital_details_list.append({
                        'name': details.get('name', 'N/A'),
                        'address': details.get('formatted_address', 'N/A'),
                        'phone': details.get('formatted_phone_number', 'N/A')
                    })
        return hospital_details_list