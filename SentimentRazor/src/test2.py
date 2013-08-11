__author__ = 'shailesh'
from nltk.tokenize import sent_tokenize
review = "I have wanted to dine here for quite some time and haven't made it yet. I just called to make a reservation" \
         " and so far they have only 1 star. The hostess was rude and did not ask any questions, but waited for me to" \
         " have to tell her everything. I paused briefly and she said, \"Hello??\" She was impatient, interrupted me to" \
         " say \"Hold Please,\" then put me on hold without asking and rushed me off the phone. I asked for a good" \
         " table since it was my dad's birthday and she begrudgingly said \"She'd put in a request.\" Total snot. So" \
         " far, NOT so good. I'm trying to get into Slanted Door(which is totally full) so I may not end up" \
         " trying this place next weekend after all."

sentences = sent_tokenize(review)
sentences = [sentences[0]] * 2 + sentences[1:]
print sentences
