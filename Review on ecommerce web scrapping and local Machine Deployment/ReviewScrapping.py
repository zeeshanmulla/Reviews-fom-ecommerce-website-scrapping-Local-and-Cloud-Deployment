from flask import Flask, render_template, url_for, request, redirect, jsonify
import requests
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)       #initializing flask app with name app


@app.route('/',methods=['POST','GET'])      #route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")      #obtaining the search string entered in the form
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost27017/")  # opening a connection to Mongo
            db = dbConn['crawlerDB']        #connecting to db called crawlerdb
            reviews = db[searchString].find({})     #searching the collection with the name same as keyword
            if reviews.count() > 0:     #if there is a collection with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews)      #show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString      #preparing the url tosearch product on flipkart
                uClient = uReq(flipkart_url)        #requesting webpage from internet
                flipkartPage = uClient.read()       #reading the webpage
                uClient.close()     #closing the connection to webserver
                flipkart_html = bs(flipkartPage, "html.parser")     #parsing the webpage as HTTP
                bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})      #searching appropriate tag to redirect to the product link
                del bigboxes[0:3]       #the first 3 members on list do not contain relevant information hence deleting them
                box = bigboxes[0]       #taking first iteration for demo
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']        #extracting actual product link
                prodRes = requests.get(productLink)     #getting product page from server
                prod_html = bs(prodRes.text, "html.parser")     #parsing product page as html
                commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})      #finding the html section containing customer comments

                table = db[searchString]        #creating a collection with same name as search string. tables and collections are analogues
                filename = searchString+".csv"      #filename to save the details
                fw = open(filename, "w")        #creating a localfile to save the details
                headers = "Product, Customer Name, Rating, Heading, Comment \n"     #providing heading of the columns
                fw.write(headers)       #writing first the header to file
                reviews = []        #initializing an empty list for reviews

                #iterating over the comment section to get the details of the customer and comments
                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text

                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'
                    fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}       #saving a detail to dictionary
                    x = table.insert_one(mydict)        #inserting the dictionary containing the review comments to the collection
                    reviews.append(mydict)      #apending comments to review list
                return render_template('results.html', reviews=reviews)     #showing review to the user
        except:
            return 'something is wrong'
            #return render_template('results.html')
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(port=8000, debug=True)      #running app on local machine on port:8000