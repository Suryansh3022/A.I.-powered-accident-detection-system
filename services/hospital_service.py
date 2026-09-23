import logging


class HospitalService:
    def __init__(self, api_key=None):
        # API key is optional for the demo version.
        self.api_key = api_key

        # Demo hospital information.
        # Replace these details with a hospital you want to show in your demo.
        self.demo_hospitals = [
            {
                "name": "Government Hospital",
                "address": "Delhi, India",
                "phone": "Demo Number"
            }
        ]

    def fetch_hospital_details_list(self, lat, lng):
        """
        Returns predefined hospital information instead of
        using the Google Places API.
        """

        logging.info(
            f"Using demo hospital data for coordinates: {lat}, {lng}"
        )

        return self.demo_hospitals    
