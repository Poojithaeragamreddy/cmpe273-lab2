# cmpe273-lab2
#Add spyne toolkit before running the python file.
pip install -r requirements.txt
#Then run the python file which fetches crime report for a location
python app.py
#When it is running successfully go to postman app in chrome and submit the url which consists of latitude,longitude and radius values
#like in below example:
Example URL :-http://localhost:8000/checkcrime?lat=37.334164&lon=-121.884301&radius=0.02
