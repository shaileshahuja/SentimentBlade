A <b><i>sentiment analysis engine</i></b>, written in <b><i>Python</i></b>.   
Given a review, the system classifies it into <b>positive</b>, <b>negative</b> or <b>neutral</b>.
It is possible to crawl reviews of a certain restaurant and get an analysis of the reviews for that restaurant. However, it is for educational purposes only, as Yelp TOC may not allow usage of their content by other parties.  
  
The other possibility is to crawl movie reviews from IMDB (<a href=https://github.com/shaileshahuja/SentimentBlade/issues/8>to be implemented</a>). 
The algorithm has been optimised for movie reviews, using an algorithm called <a href=https://github.com/shaileshahuja/SentimentBlade/issues/9>impact training</a>.
The results of impact training were facinating, as the accuracy rose from 57.15% to 91.75% of the sample movie reviews dataset.


<b>The in-depth analysis of each review includes:</b>  
1. Adjectives highlighting, thus clearly indicating where the review focuses on  
2. Scoring of each review to indicate how strongly the opinion has been presented  
3. Summary of overall scores of the restaurant    

To run, please start "<b>SentimentBlade.py</b>". Edit the URL there to crawl. To see the performance, run "<b>PerformanceTest.py</b>". You can change the dataset to be used. 
  
Have a look at the 
<a href=https://docs.google.com/file/d/0B4fGOv7vgnt9S3pJTFNENzJ3djQ/edit?usp=sharing> preliminary design</a>
and the 
<a href=https://docs.google.com/file/d/0B4fGOv7vgnt9NVU2QTJURVZmbEE/edit?usp=sharing> final report</a>.  

<b><i>Preview of how each review is analysed and broken down: <b></i>
  
![alt tag](http://i44.tinypic.com/2d6wm8i.png)
