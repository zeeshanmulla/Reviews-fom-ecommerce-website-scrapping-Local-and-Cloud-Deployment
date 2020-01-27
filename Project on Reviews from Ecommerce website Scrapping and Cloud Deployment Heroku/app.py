from flask import Flask, render_template, request, jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)       #initializing flask app with name app

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()     #cors mechanism uses add on html heaer to tell browser to give web-app run at one origin access to select resource from diff. origin
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")      #obtaining the search string entered in the form
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString      #flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)        #requesting webpage from internet
            flipkartPage = uClient.read()       #reading the webpage
            uClient.close()     #closing the connection to webserver
            flipkart_html = bs(flipkartPage, "html.parser")     #parsing the webpage as HTTP
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})      ##searching appropriate tag to redirect to the product link
            del bigboxes[0:3]       #the first 3 members on list do not contain relevant information hence deleting them
            box = bigboxes[0]       #taking first iteration for demo
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']        #extracting actual product link
            prodRes = requests.get(productLink)     #getting product page from server
            prodRes.encoding='utf-8'        #encoded into unicode transformation format
            prod_html = bs(prodRes.text, "html.parser")     #parsing product page as html
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})      #finding the html section containing customer comments

            filename = searchString + ".csv"        #filename to save the details
            fw = open(filename, "w")        #creating a localfile to save the details
            headers = "Product, Customer Name, Rating, Heading, Comment \n"     #providing heading of the columns
            fw.write(headers)       #writing first the header to file
            reviews = []        #initializing an empty list for reviews

            # iterating over the comment section to get the details of the customer and comments
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}       #saving a detail to dictionary
                reviews.append(mydict)      #apending comments to review list
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])     #showing review to the user
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)