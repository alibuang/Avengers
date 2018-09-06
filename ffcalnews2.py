from ff_econcal import getEconomicCalendar as getCal
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd

def chk_news(impact='High', window=1):
    cal_tz = timezone('US/Eastern')
    
    #generate today calendar date
    today = datetime.today()
    today = today.astimezone(cal_tz)
#    tomorrow = today + timedelta(days = 1)
    month = today.strftime("%b")
    day = str(today.day)
    year = str(today.year)
#    day_tomorrow  = str(tomorrow.day)
    
    startlink = 'calendar.php?day='+ month + day + '.' + year
    endlink = startlink
#    endlink = 'calendar.php?day='+ month + day_tomorrow + '.' + year
    
#    print('start =', startlink)
#    print ('end =', endlink)
    
    df = getCal(startlink, endlink)
#    print(df)
    
    news_df = pd.DataFrame()
    
    for i in range(len(df)):
        
        #get news datetime from dataframe
        news_dt = df.loc[i].datetime
             
        #normalize news datetime to calendar time zone
        temp_datetime = datetime.strptime(news_dt, '%Y-%m-%d %H:%M:%S')
        news_datetime = cal_tz.localize(temp_datetime) 
        
        #normalize current datetime to calendar time zone
        curr_datetime = datetime.now(cal_tz)
        
        #get window timeframe for News event
        tUpper_window = news_datetime + timedelta(hours = window)
        tLower_window = news_datetime - timedelta(hours = window)
            
        #only publish news within 1 hour before and after News
        if curr_datetime > tLower_window and curr_datetime < tUpper_window :
            
            #do not publish for Non High impact
            if df.loc[i].impact.find(impact) == -1:
                continue
            
            #save the news in news dataframe
            news_df = news_df.append(df.loc[i])
            
    news_df.reset_index(inplace=True)
        
    return news_df
            
            
if __name__ == "__main__":
   
    news_df = chk_news()
    print('\n',news_df)
    