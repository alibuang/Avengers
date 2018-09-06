from ff_econcal import getEconomicCalendar as getCal
from datetime import datetime, timedelta
from pytz import timezone
import telegram

token='488376978:AAFvFovR-Zin9VXR-AhCs0RRXXP149s_rdk'
bot = telegram.Bot(token= token)
chat_id=-1001142683257

def chk_news():
    cal_tz = timezone('US/Eastern')
    local_tz = timezone('Asia/Kuala_Lumpur')
    
    #generate today calendar date
    today = datetime.today()
    today = today.astimezone(cal_tz)
    month = today.strftime("%b")
    day = str(today.day)
    year = str(today.year)
    
    startlink = 'calendar.php?day='+month+day+'.'+year
    endlink = startlink
    
    df = getCal(startlink, endlink)
    #print(df)
    newsEvent = False
    
    chk_impact = 'High'
    window = 1
    
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
            if df.loc[i].impact.find(chk_impact) == -1:
                continue
            
            #mark there is news event
            newsEvent =  True
            
            print(news_datetime.astimezone(local_tz).strftime('%Y-%m-%d %I:%M:%S %p'), \
                  df.loc[i].currency, df.loc[i].impact, df.loc[i].event, \
                  df.loc[i].actual, df.loc[i].forecast, df.loc[i].previous)
            
#            text_msg = news_datetime.astimezone(local_tz).strftime('%Y-%m-%d %I:%M:%S %p'), \
#                        + '\n'+ df.loc[i].currency \
#                        + '\n'+ df.loc[i].impact \
#                        + '\n'+ 
                        
            text_msg = '\n'.join(['News Time: '+news_datetime.astimezone(local_tz).strftime('%Y-%m-%d %I:%M:%S %p'), \
                  'Currency: '+df.loc[i].currency, 'Impact: '+df.loc[i].impact, 'Event: '+df.loc[i].event, \
                  'Actual: '+df.loc[i].actual, 'Forecast: '+df.loc[i].forecast, 'Previous: '+df.loc[i].previous])            
            bot.send_message(chat_id=chat_id, text=text_msg, timeout=50)
            
    if not newsEvent:
        
        text = 'No ' + chk_impact + ' impact News Event passed or in 1 hour'
        print(text)
        text_msg = str(datetime.now().replace(microsecond=0)) + '\n' + text
        bot.send_message(chat_id=chat_id, text = text_msg)
            
            
if __name__ == "__main__":
   
    chk_news()
    