import environment as env
import json
import sys
import time
import timeit
import tweetpony

class JSONFetcher():
	def __init__(self, fileName):
		self.fileName = fileName + '.json'

	def fetch(self):
		print("fetching...")

		with open(self.fileName, 'rb') as f:
			for line in f:
				yield json.loads(line)

class FollowerScraper():

	def __init__(self):
		self.twitAPI = tweetpony.API(consumer_key = env.TWITTER_CONSUMER_KEY,
								consumer_secret = env.TWITTER_CONSUMER_SECRET,
								access_token = env.TWITTER_ACCESS_TOKEN_KEY, 
								access_token_secret = env.TWITTER_ACCESS_TOKEN_SECRET)

		user = self.twitAPI.user
		print ("Hello " + user.screen_name)

	def mine(self):
		nextMiningIndex = -1
		try:
			print("Searching for existing mining operation...")
			testFile = open(env.TWITTER_HANDLE + "Followers.json", 'rb')
			testFile.close()
			followers = JSONFetcher(env.TWITTER_HANDLE + "Followers")
			print("Existing mining operation found.")
			line = None
			for record in followers.fetch():
				line = record
				pass

			#print("Line: " + line['nextCursor'])
			if(line):
				nextMiningIndex = line['nextCursor']

			print ("HAMY: nextMiningIndex = " + str(nextMiningIndex))

			if( str(nextMiningIndex) == str(0) ):
				sys.exit("Existing mining operation was already completed. Exiting...")
		except IOError as err:
			print("No pre-existing mining operation found.")
			print("Beginning new expedition...")
			self.beginMining(nextMiningIndex)
		except Exception as err:
			print("ERROR: Couldn't open file")
			print(str(err))
		else:
			self.beginMining(nextMiningIndex)

	def beginMining(self, nextMiningIndex):

		if(nextMiningIndex != -1):
			outfile = open(env.TWITTER_HANDLE + "Followers.json", 'ab')
		else:
			outfile = open(env.TWITTER_HANDLE + "Followers.json", 'ab')

		while(nextMiningIndex != 0):
			#HAMYChange
			print nextMiningIndex

			fBucket = self.fetchFollowers(nextMiningIndex)

			#Check if fBucket is None
			if(fBucket):
				nextMiningIndex = fBucket['next_cursor']

				self.storeFollowers(outfile, fBucket)

	def fetchFollowers(self, nextMiningIndex):
		try:
			followerBucket = self.twitAPI.followers_ids(screen_name=env.TWITTER_HANDLE, cursor=nextMiningIndex)
		except Exception as err:
			if('88' in str(err)):
				print("Mining Suspended: Reached Twitter rate limit")
				print("Waiting 3 minutes then retrying...")
				time.sleep(180)
				self.fetchFollowers( nextMiningIndex )
			else:
				print("ERROR: Something broke when fetching followers")
				print str(err)
		else: 
			return followerBucket

	def storeFollowers(self, outfile, toStore):
		print("Iamablock")

		try:
			toWrite = {"nextCursor": toStore['next_cursor_str'], "twitterIDs": toStore['ids']}
			jsonOut = json.dumps(toWrite, separators=(',',':'))
			outfile.write(jsonOut + '\n')
		except Exception as err:
			print("ERROR: Couldn't write results")
		else:
			print("Stored followers successfully")


	def finishMining(self, outfile):
		outfile.close()


if __name__ == "__main__":

	timeStart = timeit.default_timer()
	print("Operation started at: " + repr(timeStart))

	scraper = FollowerScraper()
	scraper.mine()

	print("Operation finished")

	timeEnd = timeit.default_timer()
	print("Elapsed Time: " + repr(timeEnd - timeStart) + "s")