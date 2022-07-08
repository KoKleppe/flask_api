from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import os
import requests
import json

os.chdir('./data')

app = Flask(__name__)
api = Api(app) 

class Recommendations(Resource):
    def get(self):
        
        # Map price_range to integer
        price_range_enc = \
        {    
             '$':1
             ,'$$':2
             ,'$$$':3
        }
        
        # Read csv 
        data = pd.read_csv('data-restaurants.csv')
        
        data['price_range'] = data['price_range'].map(price_range_enc)
        
        # Add args
        parser = reqparse.RequestParser()  
        parser.add_argument('max_price_range', type=int, required=True)
        parser.add_argument('type_of_food', type=str, required=True) 
        args = parser.parse_args()
    
        # Filter data based on input max_price_range and type_of_food
        data = data[(data['price_range'] < args['max_price_range']) & (data['type_of_food'] == args['type_of_food']) ].sort_values(by=['distance_to_office', 'price_range'], ascending=True).head(5)
        
        data = data.to_dict(orient='records')
        
        return {'data': data}, 200 # Return data and 200 OK
  
class ChooseRestaurant(Resource):
    def get(self):
       
        # Read csv 
        data = pd.read_csv('data-restaurants.csv')
        
        # Add args
        parser = reqparse.RequestParser()   
        parser.add_argument('restaurant', type=str, required=True)        
        args = parser.parse_args()

        # Remove Restaurant prefix
        data = data[data['name'].str.replace('Restaurant', '').apply(str.strip) == args['restaurant']]
            
        data = data.to_dict(orient='records')
        
        payload = {"text":"Hello team. We have chosen the following restaurant for today: {} ".format(data)}
        
        # Send Slack notification
        requests.post('', json=payload) # Insert Slack Webhook URL
    
        return {'data': data}, 200 # Return data and 200 OK

# add endpoints
api.add_resource(Recommendations, '/recommendations')
api.add_resource(ChooseRestaurant, '/chooserestaurants')
        
if __name__ == '__main__':
    app.run(host='localhost', port=5000)  # Run our Flask app
    