#-*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import Word2Vec
import sys

def main(query):
	model = Word2Vec.load('ko.bin')


	#query = unicode(keyword)
	#query = u"영화"

	try:
		searched = model.most_similar(query)
		searched = [x[0] for x in searched]

		for i in range(len(searched)):
			print(searched[i])

		return searched
	except Exception:
		print('해당 단어를 이해할 수 없습니다.')
		return ''

