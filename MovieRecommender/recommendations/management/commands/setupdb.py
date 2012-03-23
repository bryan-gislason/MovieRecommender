import os
import sys
import datetime
import re

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

	_users = ''
	_items = ''
	_ratings = ''
	_months = {
		'Jan': 1,
		'Feb': 2,
		'Mar': 3,
		'Apr': 4,
		'May': 5,
		'Jun': 6,
		'Jul': 7,
		'Aug': 8,
		'Sep': 9,
		'Oct': 10,
		'Nov': 11,
		'Dec': 12
	}

	_logic = {
		'0': False,
		'1': True
	}

	def handle(self, *args, **options):

		if not len(args):
			raise CommandError("You must pass in at least one filename to import.")

		for dirname in args:
			if os.path.isfile(dirname):
				continue

			try:
				info = open(dirname + '/u.info', 'r')
				item = open(dirname + '/u.item', 'r')
				data = open(dirname + '/u.data', 'r')
			except IOError, e:
				raise CommandError(unicode(e))
			except:
				raise CommandError("Invalid data in '%s'." % dirname)

			# iterate through rows, returning each as a list that you can index
			print "Adding: '%s' to the database." % dirname

			# get info
			self._users = info.readline().split(' ')[0]
			self._items = info.readline().split(' ')[0]
			self._ratings = info.readline().split(' ')[0]
			
			# get items
			for line in xrange(int(self._items)):
				self.add_item_row_to_db(item.readline())

			# calculate similarities
			movie_ratings = self.get_movie_ratings(data)
			self.pearson_correlation(movie_ratings)

			return

			# get users and their ratings
			#for line in range(int(self._ratings)):
			#	self.add_data_row_to_db(data.readline())
			
	def add_item_row_to_db(self, row):
		from recommendations.models import Movie
		print row
		row = row.split('|')
		try:
			release_date = re.search('\([0-9]{4}\)', row[1].strip()).group(0).strip('(').strip(')')
		except:
			return
		video_release_date = row[2].split('-')

		try:
			Movie.objects.get(pk=row[0])
		except Movie.DoesNotExist:
			movie = Movie.objects.get_or_create(
	            movie_id=row[0],
	            title = unicode(row[1].strip().split(' ')[:-1][0], 'latin-1'),
			    release_date = datetime.date(int(release_date),	1, 1),
			    video_release_date = datetime.date(
							    		int(video_release_date[2]),
							    		self._months[video_release_date[1]],
							    		int(video_release_date[0])
			    					),
			    imbd_url = row[4],
			    unknown = self._logic[row[5]],
			    action = self._logic[row[6]],
			    adventure = self._logic[row[7]],
			    animation = self._logic[row[8]],
			    childrens = self._logic[row[9]],
			    comedy = self._logic[row[10]],
			    crime = self._logic[row[11]],
			    documentary = self._logic[row[12]],
			    drama = self._logic[row[13]],
			    fantasy = self._logic[row[14]],
			    film_noir = self._logic[row[15]],
			    horror = self._logic[row[16]],
			    musical = self._logic[row[17]],
			    mystery = self._logic[row[18]],
			    romance = self._logic[row[19]],
			    sci_fi = self._logic[row[20]],
			    thriller = self._logic[row[21]],
			    war = self._logic[row[22]],
			    western = self._logic[row[23][0]],
	        )

	def get_movie_ratings(self, datafile):
		from decimal import Decimal 

		movie_ratings = {}
		for line in xrange(int(self._ratings)):
			row = datafile.readline()
			row_data = row.strip().split('\t')
			try:
				# movie_id is in second place ([1])
				movie_ratings[row_data[1]] # does movie_id exist yet?
				try:
					movie_ratings[row_data[1]][row_data[0]] = Decimal(row_data[2])
				except:
					continue
			except:
				movie_ratings[row_data[1]] = {row_data[0]: Decimal(row_data[2])} # create proper dicts

		return movie_ratings

	def pearson_correlation(self, movie_ratings):
		from recommendations.models import Movie, Similarity
		from decimal import Decimal 
		from math import sqrt

		# calculation
		for mov2_i in xrange(int(self._ratings)):
			# x and y are ratings for different movies by the same user
			for movie_id, unique_user_ratings in movie_ratings.iteritems():
				# look at one movie and get similarity between another movie
				x_ratings = []
				y_ratings = []

				# get ratings/mean_ratings from common users from the compared movies
				for u_id, x_rating in unique_user_ratings.iteritems():
					try:
						y_rating = movie_ratings[str(mov2_i)][str(u_id)]
					except:
						continue
					x_ratings.append(x_rating)
					y_ratings.append(y_rating)
				
				if len(x_ratings) == 0:
					continue

				x_mean = Decimal(sum(x_ratings)) / Decimal(len(x_ratings))
				y_mean = Decimal(sum(y_ratings)) / Decimal(len(y_ratings))

				top_sum = 0
				x_bot_sum = 0
				y_bot_sum = 0

				# compute similarity
				for i in range(len(x_ratings)):
					A = (x_ratings[i] - x_mean)
					B = (y_ratings[i] - y_mean)
					top_sum += top_sum + (A * B)
					x_bot_sum += x_bot_sum + pow(A, 2)
					y_bot_sum += y_bot_sum + pow(B, 2)

				if y_bot_sum == 0 or x_bot_sum == 0:
					continue
				result = Decimal(top_sum) / Decimal(sqrt(x_bot_sum)*sqrt(y_bot_sum))

				print "sim %s, %s = %f" % (movie_id, mov2_i, result)
				
				try:
					sim = Similarity.objects.get(
						movie_id = movie_id
					)
				except Similarity.DoesNotExist:
					sim = Similarity.objects.create(
						movie_id = movie_id,
						value = result
					)

					Movie.objects.get(pk=mov2_i).similarity.add(sim)
		return

	def add_data_row_to_db(self, row):
		from recommendations.models import UserProfile, Rating 
		print 'importing data'
