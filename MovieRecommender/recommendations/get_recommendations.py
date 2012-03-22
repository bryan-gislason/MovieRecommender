# create recommendations

# use user = request.user

from django.db import *
from django.contrib.auth.models import User
from recommendations.models import Movie, Rating, Similarity
from decimal import Decimal

def setup():
	user, res = User.objects.get_or_create(username='Bryan')

	mov_id = 1
	rating = Rating.objects.create(user=user, movie_id=mov_id,rating=4) # rate 'toy story' : 4

	return

def get_recommendations():
	user = User.objects.get(username='Bryan')
	user_ratings = Rating.objects.filter(user=user, rating__isnull=False) # get ratings that have rating value
	print "user's ratings: %s" % user_ratings

	movie_ids = [rating.movie_id for rating in user_ratings]
	for movie in Movie.objects.exclude(movie_id__in=movie_ids):

		top_sum = 0
		bottom_sum = 0
		for user_rating in user_ratings:
			# currently only one rating
			movie_id = user_rating.movie_id
			rating_value = user_rating.rating

			try:
				sim_value = movie.similarity.get(pk=movie_id)[0].value
				print 'sim_value %f' % sim_value
			except:
				continue
			print rating_value, sim_value
			top_sum = top_sum + (rating_value * sim_value)
			bottom_sum = bottom_sum + sim_value

		if bottom_sum == 0:
			continue

		suggested_rating = Decimal(top_sum)/Decimal(bottom_sum)
		new_or_old_rating, res = Rating.objects.get_or_create(user=user, movie_id=movie.movie_id)
		new_or_old_rating.suggested_rating = suggested_rating

		print "movie: %s , suggested_rating: %s" % (movie.title, suggested_rating)

	return