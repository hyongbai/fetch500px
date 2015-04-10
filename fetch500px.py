import urllib
import urllib2
import json  
import datetime
import os
import time
from multiprocessing.dummy import Pool as ThreadPool 


IMAGE_500PX_SIZE=1 #2048
PAGE_500PX_SIZE=100
BASE_500PX_URL="https://api.500px.com/v1/photos"
CONSUMER_KEY="7;uyCG<r}8a)s2cH$xg\"c_+4'\"73G#r4K@!f);rA"
# ROT47_ENCODED_500PX_CK="fjFJrvkCNg2XDa4wSI8Q40ZcVQfbvRCczoP7XjCp"
ROT47_ENCODED_500PX_CK="CzuGAezTrh4xSkxlu8At1C0nt11rQe58kx29kkrE"
FEATURES_500="popular\
highest_rated\
upcoming\
editors\
fresh_today\
fresh_yesterday\
fresh_week"
CATEGORIES_500="{\
\"0\":\"Uncategorized\",\
\"10\":\"Abstract\",\
\"11\":\"Animals\",\
\"5\":\"Black and White\",\
\"1\":\"Celebrities\",\
\"9\":\"City and Architecture\",\
\"15\":\"Commercial\",\
\"16\":\"Concert\",\
\"20\":\"Family\",\
\"14\":\"Fashion\",\
\"2\":\"Film\",\
\"24\":\"Fine Art\",\
\"23\":\"Food\",\
\"3\":\"Journalism\",\
\"8\":\"Landscapes\",\
\"12\":\"Macro\",\
\"18\":\"Nature\",\
\"4\":\"Nude\",\
\"7\":\"People\",\
\"19\":\"Performing Arts\",\
\"17\":\"Sport\",\
\"6\":\"Still Life\",\
\"21\":\"Street\",\
\"26\":\"Transportation\",\
\"13\":\"Travel\",\
\"22\":\"Underwater\",\
\"27\":\"Urban Exploration\",\
\"25\":\"Wedding\"\
}"

BASE_500PX_DL_DIR="500px"
# #print CATEGORIES_500
CATEGORIES_DICT=json.loads(CATEGORIES_500)
DAY_STR=datetime.date.today().strftime("%Y%m%d")
DOWNLOADED_IMAGE=0

class Photo :
	#from collections import namedtuple 
	def __init__(self, _id, url, category, _format, name):
		self._id = _id
		self.url = url
		self.category = category
		self._format = _format
		self.name = name

	def __str__(self):
		return "[id="+str(self._id)\
		+"] [url="+self.url\
		+"] [category="+str(self.category)\
		+"] [format="+self._format\
		+"] [name="+self.name\
		+ "]"


# def Photo_decoder(obj):
#     if '__type__' in obj and obj['__type__'] == 'Photo':
#         return User(obj['name'], obj['username'])
#     return obj

def parse_500_photos(json_str):
	jobj = json.loads(json_str)
	json_list = jobj["photos"]
	photo_list = []
	for pho in json_list:
		p = Photo(pho["id"], pho["image_url"], pho["category"], pho["image_format"], pho["name"])
		# #print p._id
		photo_list.append(p)

	# #print str(photo_list)
	return photo_list

def dl_single_photo(pho):
	category = CATEGORIES_DICT[str(pho.category)]
	parent_dir = BASE_500PX_DL_DIR+"/"+DAY_STR+"/"+category
	# {id}_{name}.{format}
	file_name = str(pho._id)+"."+pho._format #"_"+pho.name+
	file_path = parent_dir +"/"+ file_name
	image_url=pho.url
	#
	if  not os.path.exists(parent_dir) :
		os.makedirs(parent_dir)
	#
	if  os.path.exists(file_path) :
		#print file_path+"	existed"
		return 0
	#
	#print "Downloading to \""+file_path+"\""
	# print "Downloaded="+str(DOWNLOADED_IMAGE)+
	print "	Downloading " + str(pho._id)+"."+pho._format
	# download
	try:
		urllib.urlretrieve(pho.url , file_path)
		# curl image_url -o file_path
	except Exception, e:
		print "Fail to download " + pho.url
		print e
		time.sleep(5)
		dl_single_photo(pho)
	# DOWNLOADED_IMAGE = DOWNLOADED_IMAGE + 1

	print "	Downloaded " + str(pho._id)+"."+pho._format
	return 1

def dl_photos(photos):

	if len(photos) == 0:
		return

	# Make the Pool of workers
	pool = ThreadPool(8) 
	# Open the urls in their own threads
	# and return the results
	results = pool.map(dl_single_photo, photos)
	#close the pool and wait for the work to finish 
	pool.close() 
	pool.join() 

	# for pho in photos:
	# 	dl_single_photo(pho)



def fetch_500_json(cur_page):
	# prepare URL
	URL=BASE_500PX_URL+'?sort=created_at'
	# URL=URL+'&only=Abstract'
	URL=URL+'&feature=fresh_today'
	URL=URL+'&consumer_key='+ROT47_ENCODED_500PX_CK
	URL=URL+'&image_size='+str(IMAGE_500PX_SIZE)
	URL=URL+'&rpp='+str(PAGE_500PX_SIZE)
	URL=URL+'&page='+str(cur_page)

	print "fetch_500_json " + URL
	# request
	req = urllib2.Request(URL)
	res_data = urllib2.urlopen(req)
	res = res_data.read()
	#print res
	return res

def dl_500px_image(start):
	current_page = 1
	total_pages = current_page

	while current_page <= total_pages:
		try:
			#fetching
			raw_500 = fetch_500_json(current_page)
			#photo list
			photo_list = parse_500_photos(raw_500)
			#
			total_pages = json.loads(raw_500)["total_pages"]
			#
			#print str(current_page)+" / "+str(total_pages)
			#download
			dl_photos(photo_list)
			#
		except Exception, e:
			print "Fail to fetch json:"
			print e
			time.sleep(5)
		else:
			current_page =  current_page + 1
	time.sleep(3600)
	dl_500px_image(0)

def main():
	# fetch_500_json(1)
	dl_500px_image(0)


if __name__ == "__main__":
	main()

