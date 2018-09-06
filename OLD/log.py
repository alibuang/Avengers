from datetime import datetime


def Log(txt):
    
    file = open('avenger.log','a')
    file.write('\n')
    
    header = str(datetime.now().replace(microsecond=0)) + '|'
    file.write(header)
    file.write(txt)
    file.close()
    
Log('aisy' + 23)
