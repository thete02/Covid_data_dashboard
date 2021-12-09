from flask import render_template
from flask import Flask
from flask import request
import time, pyttsx3, json, sched
app = Flask(__name__)
log = open("log.txt","a") 
with open("config.json", "r") as config:
    config_dict = json.load(config)
seen = []
updates_cancelled = ""
updates = []
updates_events = []
s = sched.scheduler(time.time, time.sleep)
s.run(blocking=False)
@app.route("/index")

def hello():
    log.write("page reloaded")
    update_interval = request.args.get("update")
    update_name = request.args.get("two")
    repeat = request.args.get("repeat")
    notif = request.args.get("notif")
    update_cancelled = request.args.get("update_item")
    if not update_cancelled == None:
        update_canceller(update_cancelled)               
    if request.args.get("covid-data") == "covid-data":
        schedule_covid_updates(update_interval,update_name,repeat)
    if request.args.get("news") == "news":
        schedule_news_updates(update_interval,update_name,repeat)
    if not notif == None:
        news_update(False, notif)    
    return update()

def update_canceller(update_cancelled):
    for update_items_events in updates_events:
        if update_cancelled == update_items_events[0]: 
            s.cancel(update_items_events[1])
            for count in range(0,len(updates),1):
                if updates[count]["title"] ==  update_items_events[0]:
                    del updates[count]
                    

def update():
    from datetime import datetime
    csv_to_json_saver(covid_API_request(config_dict["localauth"],"ltla"))
    csv_to_json_saver(covid_API_request(config_dict["nation"],"nation"))
    

    localfilename = "ltla_"+(datetime.today().strftime("%Y-%m-%d"))+".csv"
    nationalfilename = "nation_"+(datetime.today().strftime("%Y-%m-%d"))+".csv"

    x,local_7day_infections,y = process_covid_csv_data(parse_csv_data(localfilename))
    deaths_total,national_7day_infections,hospital_cases = process_covid_csv_data(parse_csv_data(nationalfilename))
    
    
    location = config_dict["localauth"]
    nation_location = config_dict["nation"] 

    

    news = news_API_request()

    log.write("updates ran")
    return render_template("index.html",updates=updates, title="Jack's covid app",location=location,local_7day_infections=local_7day_infections,nation_location=nation_location,hospital_cases=hospital_cases,deaths_total=deaths_total,national_7day_infections=national_7day_infections,news_articles=news)

def schedule_covid_updates(update_interval, update_name, repeating=False):
    if update_interval == None and update_name == None and repeating == None:
        return False

    else:        
        update_secs, update_time = update_interval_formatter(update_interval)
        content = "Scheduled for "+str(update_time)
        updates.append({"title":update_name,"content":content})
        e1 = s.enter(update_secs,1,covid_update,(repeating))
        updates_events.append([update_name,e1])
        log.write("covid update scheduled")
              
def schedule_news_updates(update_interval, update_name, repeating=False):
    if update_interval == None and update_name == None and repeating == None:
        return False

    else:
        update_secs, update_time = update_interval_formatter(update_interval)
        content = "Scheduled for "+str(update_time)
        updates.append({"title":update_name,"content":content}) 
        e1 = s.enter(update_secs,1,news_update,(repeating))
        updates_events.append([update_name,e1])
        log.write("news update scheduled")

      
def update_interval_formatter(update_time):
    from datetime import datetime
    now = datetime.now()
    currtime = now.strftime("%H:%M").split(":")
    update = update_time.split(":")

    if currtime[0] > update[0]:
        time_to_mid = 24*60*60 - hhmm_to_seconds((str(currtime[0]+":"+currtime[1])))
        update_secs = time_to_mid + hhmm_to_seconds(update_time)
    elif currtime[0] == update[0]:
        if currtime[1] > update[1]:
            time_to_mid = 24*60*60 - hhmm_to_seconds((str(currtime[0]+":"+currtime[1])))
            update_secs = time_to_mid + hhmm_to_seconds(update_time)
        elif currtime[1] < update[1]:
            m = int(update[1]) - int(currtime[1])
            update_secs = m *60
        else:
            update_secs = 24*60*60
    elif currtime[0] < update[0]:
        update_secs = int(hhmm_to_seconds(update_time)) - int(hhmm_to_seconds((str(currtime[0]+":"+currtime[1]))))
    return update_secs, update_time

def hhmm_to_seconds(hhmm):
    s = int((60*60*int(hhmm.split(':')[0]))+(60*int(hhmm.split(':')[1])))
    return s


def covid_update(repeat=False):
    from datetime import datetime
    if repeat:
        e1 = s.enter(86400,1,covid_update,(True))
    
    csv_to_json_saver(covid_API_request(config_dict["localauth"],"ltla"))
    csv_to_json_saver(covid_API_request(config_dict["nation"],"nation"))
    

    localfilename = "ltla_"+(datetime.today().strftime("%Y-%m-%d"))+".csv"
    nationalfilename = "nation_"+(datetime.today().strftime("%Y-%m-%d"))+".csv"

    x,local_7day_infections,y = process_covid_csv_data(parse_csv_data(localfilename))
    deaths_total,national_7day_infections,hospital_cases = process_covid_csv_data(parse_csv_data(nationalfilename))
    
    
    location = config_dict["localauth"]
    nation_location = config_dict["nation"] 

    log.write("covid stats updated")
    
    
    return render_template("index.html",title="Jack's covid app",location=location,local_7day_infections=local_7day_infections,nation_location=nation_location,hospital_cases=hospital_cases,deaths_total=deaths_total,national_7day_infections=national_7day_infections)


def news_update(repeat=False,notif=None):
    if repeat:
        e1 = s.enter(86400,1,news_update,(True))
    if not notif == None:
        seen.append(notif)
    
    news = news_API_request()

    log.write("news articles updated")
    
    return render_template("index.html",news_articles=news)
    

def covid_API_request(location=  "Exeter",location_type = "ltla"):
    import csv
    from uk_covid19 import Cov19API
    from json import dumps
    from requests import get
    from datetime import datetime

    ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"
    AREA_TYPE = location_type
    AREA_NAME = location
    

    filters = [
    f"areaType={ AREA_TYPE }",
    f"areaName={ AREA_NAME }"
    ]
    

    structure = {
    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }

      
    api_params = {
    "filters": str.join(";", filters),
    "structure": dumps(structure, separators=(",", ":"))
    }   
    
    response = get(ENDPOINT, params=api_params, timeout=10)
    dict_data = response.json()

    log.write("covid api request")
    
    return dict_data

def csv_to_json_saver(dict_data):

    import csv
    from datetime import datetime

    name = datetime.today().strftime("%Y-%m-%d")

    csv_file = dict_data["data"][0]["areaType"]+"_"+name+".csv"
    

    headerdict = str((list(dict_data["requestPayload"]["structure"].keys())))[1:-1].replace("'","").replace(" ","")
    data_to_write = ""
    try:
        with open(csv_file, "w") as csvfile:
            csvfile.write(headerdict+"\n")
            for count in range(len(dict_data["data"])):
                for data in dict_data["data"][count]:
                    if not dict_data["data"][count][data] == None:
                        data_to_write = data_to_write + str(dict_data["data"][count][data])+","
                    else:
                        data_to_write = data_to_write + ","
                data_to_write = data_to_write[:-1]+"\n"
                csvfile.write(data_to_write)
                data_to_write = ""
                
            
    except IOError:
        print("I/O error")




def parse_csv_data(csv_filename):
    import csv
    
    csv_file = open(csv_filename)
    arr = list(csv.reader(csv_file))
    return arr


def process_covid_csv_data(covid_csv_data):

    death_count = 0
    x = 1
    blank = True
    while blank == True:
        if not x > len(covid_csv_data)-1:
            if not covid_csv_data[x][4] == "" and covid_csv_data[x][4].isnumeric():
                blank = False
                death_count = int(covid_csv_data[x][4])
        else:
            blank = False
            death_count = -1
        x += 1

    case_7day_count = 0
    for count in range(2,8):
        if not covid_csv_data[count][6] == "":
            case_7day_count += int(covid_csv_data[count][6])

    if not covid_csv_data[1][5] == "":
        hosptial_cases = covid_csv_data[1][5]
    else:
        hosptial_cases = -1
    
    return death_count, case_7day_count, hosptial_cases


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):

    import requests, json

    covid_terms = covid_terms.split(" ")


    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = config_dict["newsAPIkey"]
    country = config_dict["newsAPInation"]
    complete_url = base_url + "country=" + country + "&apiKey=" + api_key
    response = requests.get(complete_url)
    x = response.json()

    with open("news.json", "w") as f:
        json.dump(x, f)

    
    filtered_articles = []
    with open("news.json", "r") as f:
        news_dict = json.load(f)
        articles = news_dict["articles"]
        for article in articles:
            for covid_term in covid_terms:
                if covid_term in article["title"]:
                    filtered_articles.append(article)

    appearances = 0

    for item1 in filtered_articles:
        title_to_check = item1["title"]
        for item2 in filtered_articles:
            if title_to_check == item2["title"]:
                appearances += 1
            if appearances == 2:
                del filtered_articles[filtered_articles.index(item2)]
        appearances = 0
    
    sub_final_list = []
    for item in filtered_articles:
        a = {"title":None,"content":None}
        a["title"] = item["title"]
        a["content"] = item["content"]
        sub_final_list.append(a)
    
    to_go = []
    
    for items in sub_final_list:
        for title in seen:            
            if items["title"] == title:
                try:
                    a = sub_final_list.index(items)
                    to_go.append(a)
                except ValueError:
                    print("Item already removed")
    final_list = [v for i, v in enumerate(sub_final_list) if i not in to_go]


    log.write("news articles request")
    
    return final_list



if __name__ == "__main__":
    app.run()
