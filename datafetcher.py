import bs4
import re

def scrape_attendance_all(source):
	soup = bs4.BeautifulSoup(source, 'lxml')
	table=soup.tbody
	rows = table.find_all("tr")
	rows_list = []
	for row in rows:
	 temp_list = []
	 columns = row.find_all("td")
	 for column in columns:
	  temp_list.append(column.get_text())
	 rows_list.append(temp_list)
	message=""
	for row in range(3,len(rows_list)-1):
	 for column in range(0,len(rows_list[2])):
	  message +=(rows_list[2][column]+':'+rows_list[row][column])+'\n'
	 message += '\n\n'

	return message

def scrape_marks_all(source):
	soup = bs4.BeautifulSoup(source, 'lxml')
	table=soup.table
	message=""
	rows = table.find_all("tr")
	rows_list = []
	for row in rows:
	 temp_list = []
	 columns = row.find_all("td")
	 for column in columns:
	  temp_list.append(column.get_text())
	 rows_list.append(temp_list)
	message+= (rows_list[2][0]+'\n')
	for row in range(3,len(rows_list)):
	 for column in range(0,len(rows_list[3])):
	  message +=(rows_list[1][column]+':'+rows_list[row][column])+'\n'
	 message += '\n'
	return message

def scrape_attendance_subject(source,subject):
	soup = bs4.BeautifulSoup(source, 'lxml')
	table=soup.tbody
	rows = table.find_all("tr")
	rows_list = []
	for row in rows:
	 temp_list = []
	 columns = row.find_all("td")
	 for column in columns:
	  temp_list.append(column.get_text())
	 rows_list.append(temp_list)
	message=""
	for row in range(3,len(rows_list)-1):
	 if(subject.lower().strip() == (rows_list[row][1]).lower().strip()):
	  for column in range(0,len(rows_list[2])):
	   message +=(rows_list[2][column]+':'+rows_list[row][column])+'\n'
	  message += '\n\n'
	  break;
	if(len(message) < 5):
		message = "Couldn't find a subject with this name."
	return message

def validate_registration(source):
	soup = bs4.BeautifulSoup(source, 'lxml')
	tr = soup.find('tr')
	td_list = tr.find_all("td")
	return td_list[0].text.strip()[8:-12] 

#https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
def multireplace(string, replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], string)

def scrape_timetable_all(source):
	soup = bs4.BeautifulSoup(source, 'lxml')
	tables = soup.find_all('tbody')
	table_subcode_rows = tables[0].find_all('tr')
	table_subname_rows = tables[1].find_all('tr')
	dict_subname={}
	for row in table_subname_rows:
		columns = row.find_all('td')
		for column in xrange(0,len(columns)-1,2):
			dict_subname[columns[column].get_text().strip()] = columns[column+1].get_text().strip()
	rows_list = []
	for row in table_subcode_rows:
		 temp_list = []
		 columns = row.find_all('td')
		 for column in columns:
			temp_list.append(column.get_text())
		 rows_list.append(temp_list)
	message=''
	for row in range(3,len(rows_list)):
		message += rows_list[row][0]+'\n'
		for column in range(1,len(rows_list[3])):
			x = rows_list[row][column]
			message += rows_list[2][column-1]+' : '+ multireplace(x,dict_subname) + '\n'
		message += '\n'
	return message
