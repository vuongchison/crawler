# -*- coding: utf-8 -*-
import scrapy
import json
import http.client
import sqlite3


class HackerrankSpider(scrapy.Spider):
    name = 'hackerrank'
    sqlConn = sqlite3.connect('hackerrank.db')
    c = sqlConn.cursor()
   
    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

        # Tạo bảng
        self.c.execute("""DROP TABLE IF EXISTS problem;""")
        self.c.execute("""CREATE TABLE problem( 
                    id int primary key, 
                    name varchar(255) not null, 
                    slug varchar(255)  not null, 
                    preview text , 
                    max_score int , 
                    total_count int , 
                    solved_count int ,
                    challenge_problem_statement_body text ,
                    challenge_sample_input_body text ,
                    challenge_sample_output_body text ,
                    challenge_explanation_body text );
                    """)
        self.sqlConn.commit()

        # Kết nối đến hackerrank.com
        httpConn = http.client.HTTPSConnection("www.hackerrank.com")
        print("OK")

        # Lấy danh sách các bài toán về
        i = 0
        while True:
            URL = "/rest/contests/master/tracks/algorithms/challenges?offset=" + str(i) + "&limit=10&track_login=true"
            httpConn.request("GET", URL)
            r = httpConn.getresponse()
            if (r.status != 200):
                break
            j = json.loads(r.read())
            for problem in j["models"]:
                print(i)
                
                insertQuery = """insert into problem (id, name, slug, preview, max_score, total_count, solved_count)
                values (%s, '%s', '%s', '%s', %s, %s, %s);""" % (problem["id"], problem["name"].replace("'", "''"), problem["slug"].replace("'", "''"), problem["preview"].replace("'", "''"), problem["max_score"], problem["total_count"], problem["solved_count"])
                self.c.execute(insertQuery)

                yield scrapy.Request('http://www.hackerrank.com/challenges/' + problem["slug"] + '/problem', callback=self.parse, headers=headers)
                
            self.sqlConn.commit()    
            i += 10

        httpConn.close()

        self.sqlConn.commit()
       


    def parse(self, response):
    	
        print("\n\n\nparse\n\n\n")

        challenge_problem_statement_body = ''.join(response.css('.challenge_problem_statement_body p, .challenge_problem_statement_body ul').extract()).replace("'", "''")
        challenge_sample_input_body = ''.join(response.css('.challenge_sample_input_body code').extract()).replace("'", "''")
        challenge_sample_output_body = ''.join(response.css('.challenge_sample_output_body code').extract()).replace("'", "''")
        challenge_explanation_body = ''.join(response.css('.challenge_explanation_body p').extract()).replace("'", "''")

        updateQuery = """UPDATE problem SET challenge_problem_statement_body = '%s', challenge_sample_input_body = '%s', challenge_sample_output_body = '%s', challenge_explanation_body = '%s' WHERE slug = '%s';
        """ % (challenge_problem_statement_body, challenge_sample_input_body, challenge_sample_output_body, challenge_explanation_body, response.url.split("/")[-2])
        self.c.execute(updateQuery)

        print("\n\n\n")
