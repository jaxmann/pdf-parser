import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from watson_developer_cloud import AlchemyLanguageV1
import unirest
import csv
import os

g=open(sys.argv[1],"w")
w=csv.writer(g, lineterminator='\n')
w.writerow(('option1','option2','option3','option4','option5','option6', 'option7','total_points','comment','comment_sent_type','comment_sent_score'))


for filename in os.listdir("./pdfFiles"):
	fp = open("./pdfFiles/" + filename, "rb")
	parser = PDFParser(fp)
	doc = PDFDocument(parser)

	questions = ["1", "2", "3", "4", "5", "6", "7", "8"]
	comments = ["", "", "", "", ""]
	points = 0

	print "Fetching Survey data..."
	options = []
	fields = resolve1(doc.catalog['AcroForm'])['Fields']
	for i in fields:
		field = resolve1(i)
		name, value = field.get('T'), field.get('V')
		if name in questions:
			option = str(value).replace("Yes", "Never")
			if option == "/Always": 
				points = points + 3
				options.append('3')
			if option == "/Often": 
				points = points + 2
				options.append('2')
			if option == "/Seldom": 
				points = points + 1
				options.append('1')
			if option == "/Never": 
				points = points + 0
				options.append('0')
			print name + ": " + option[1:]
		elif "Comments" in name:
			comments[int(name[-1]) - 1] = str(value)

	print "Total Points: " + str(points) + "/" + str((len(questions) - 1) * 3) + "\n"
	total_points = points

	finalComment = ""
	for comment in comments:
		if comment == "None": comment = ""
		finalComment += comment + " "

	print "Comment: " + finalComment + "\n"
	comment = finalComment

	fp.close()

	response = unirest.post("https://twinword-sentiment-analysis.p.mashape.com/analyze/",
	headers = {
			"X-Mashape-Key": "51Eq08jPLxmsh8Oe2heKA03hyx0Kp15rexIjsnTeObVaxJIJ2v",
			"Content-Type": "application/x-www-form-urlencoded",
			"Accept": "application/json"
		},
	params = {
			"text": finalComment
		}
	)
	print("Comment Sentiment: ")
	print(response.body['type'])
	comment_sent_type = response.body['type']
	print(format(response.body['score']*100, '2.4f')) #print to 4 decimal places
	comment_sent_score = format(response.body['score']*100, '2.4f')

	w.writerow((
        options[0],
        options[1],
        options[2],
        options[3],
        options[4],
        options[5],
        options[6],
        total_points,
        comment,
        comment_sent_type,
        comment_sent_score
    ))

