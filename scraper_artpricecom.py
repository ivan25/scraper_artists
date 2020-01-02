import scrapy, json, random, re

class ScraperArtpriceCom(scrapy.Spider):
	name = 'ScraperArtpriceCom'
	allowed_domains = ['www.artprice.com']
	custom_settings = {'DOWNLOAD_DELAY': 30, 'RANDOMIZE_DOWNLOAD_DELAY': True, 
						'USER_AGENT': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'}

	start_urls = ['https://www.artprice.com/artists/all/'+i for i in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')]

	def parse(self, response):
		for url_i in response.xpath('//a/@href'):
			if re.match(r'/artists/all/[A-Z]/[A-Z]{3}/[A-Z]{3}', url_i.extract()):
			
				# load the list with the pages already downloaded
				with open('done_artpricecom.json', 'r') as f: 
					list_done = json.load(f)

				if url_i.extract() not in list_done:
					yield scrapy.Request('https://www.artprice.com' + url_i.extract(), 
											callback=self.parse_3gram,
											meta={'url_i': url_i.extract()})

	def parse_3gram(self, response):
		for url_i in response.xpath('//a'):
			if re.match(r'^/artist/', url_i.xpath('@href').extract_first()):
				text_i = ' '.join(url_i.xpath('text()').extract()).strip()

				search_date = re.search('(\([\w\-\.\?\/]*\))$', text_i)
				if search_date:
					date = search_date.group(0).strip().replace('(', '').replace(')', '').strip()
					artist = text_i.replace(date, '').replace('()', '').strip()
				else:
					date = ''
					artist = text_i

				yield {
					'ARTIST': artist, 
					'DATE': date, 
					'URL': url_i.xpath('@href').extract_first().replace('/artist/', '')
				}
				
		# update the list with the pages already downloaded
		with open('done_artpricecom.json', 'r') as f: 
			list_done = json.load(f)
			
		list_done.append(response.meta['url_i'])
		
		with open('done_artpricecom.json', 'w') as f: 
			json.dump(list_done, f, indent=2)
