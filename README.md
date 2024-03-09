﻿# FRIENDLY_SOLAR_SHOWCASE
## Overview
This project is a Solar Energy Prediction and Management System designed to help users estimate solar irradiance at their location and manage their energy consumption through weekly planners and appliance management.

## Features
- **Solar Energy Prediction**: Users can input their latitude and longitude to predict solar irradiance for the next 7 days.
- **User Profiles**: Users can create profiles with their location coordinates and panel information.
- **Weekly Planners**: Users can create and manage weekly planners to schedule energy-consuming activities.
- **Appliance Management**: Users can add appliances to their profiles and assign them to weekly planners.

## Important

For the purposes of the demonstration, the exact implementation of the data processing and the use of an ensemble of hybrid neural network models for irradiance prediction have been hidden.

## Installation
1. Clone the repository:

git clone https://github.com/yourusername/solar-energy-management.git
cd solar-energy-management


2. Create a virtual environment:

python3 -m venv env
source env/bin/activate # For Unix/macOS
env\Scripts\activate # For Windows


3. Install dependencies:

pip install -r requirements.txt


4. Apply database migrations:

python manage.py migrate


5. Run the development server:

python manage.py runserver


6. Access the application at `http://localhost:8000` in your web browser.

## Usage
1. **Solar Energy Prediction**:
- Navigate to the prediction page and enter your latitude and longitude to get solar irradiance predictions for the next 7 days.

2. **User Profiles**:
- Create or update your user profile with location coordinates and panel information.

3. **Weekly Planners**:
- Create and manage weekly planners to schedule energy-consuming activities.

4. **Appliance Management**:
- Add appliances to your profile and assign them to weekly planners.

## Testing
Run the test suite to ensure the application works as expected:

python manage.py test


## Credits
This project was developed by Kacper M. Książek.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Certain components of this project may be licensed under Creative Commons (CC), mainly:
- For content from [Open Meteo](https://open-meteo.com/):
  Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

- For content from [Europeana](https://www.europeana.eu/pl/item/2022502/_KAMRA_309879):
  Licensed under [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/).

- For content from [SimpleMaps](https://simplemaps.com/data/world-cities):
  Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

 
