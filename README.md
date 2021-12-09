# Covid_data_dashboard
A web application, that displays covid statistics relevant to your location, and covid related news items.

To run the covid dashboard, just double click on "COVID dashboard.py" and allow it to run, it should then display:
 * Serving Flask app 'COVID dashboard' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

This shows that it is working.
Then, go into your browser of choice and enter the url "127.0.0.1:5000/index", this will then display the covid dashboard.

To set up an update, just type in the time you'd wish it to request for either a covid data or a news article update (specify which or both underneath using the checkboxes), then give the update a label and it should appear on the webpage.
Then to cancel the update, simply cross off it's box in the top left.

To delete news articles you've already seen, simply cross them off and they should not appear again.


It should then display covid statistics relevant to your location, defaulting to exeter, the config.json file is fully customisable.
To change your local area, just change the "localauth" key's value from the defualt Exeter to your location, e.g, "portsmouth".
The same applies to your nation in the UK, the "nation" key's value can be changed to any of the four nations, e.g, "Scotland".
You can also change the country the news api requests for, change the "newsAPInation" key's value to any other country code, e.g, "us"
The key to the news api is also stored in the config.json file, if you wish to change this to your own, just replace the value.

