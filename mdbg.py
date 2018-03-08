from urllib.request import urlopen, urlretrieve
from html.parser import HTMLParser
import urllib.parse
import re

def get_url(sign):
  url = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdqb=" \
     + urllib.parse.quote(sign)
  return url

class Word():
  defs = []
  pinyin = ""
  pinyin_code = ""
  sign = ""

  def save_all(self):
    try:
      self.save_info()
      print("Saved translation.")
    except:
      print("Found no translation.")
    try:
      self.save_sound()
      print("Saved pronounciation.")
    except:
      print("Found no pronounciation.")
    try:
      self.save_strokes()
      print("Saved strokes.")
    except:
      print("Found no strokes.")

  def save_sound(self):
    url = "https://www.mdbg.net/chinese/rsc/audio/voice_pinyin_pz/{}.mp3" \
        .format(self.pinyin_code.lower())
    urlretrieve(url, self.sign + ".mp3")

  def save_info(self):
    assert(self.pinyin != "")
    assert(self.sign != "")
    assert(self.defs != [])
    file = open(self.sign + ".txt", "w")
    file.write(self.sign + "\n")
    file.write(self.pinyin + "\n")
    file.write(" / ".join(self.defs) + "\n")
    file.close()

  def save_strokes(self):
    url = "https://www.mdbg.net/chinese/dictionary-ajax?c=cdqchi&i={}" \
        .format(urllib.parse.quote(self.sign))
    html = urlopen(url).read().decode('utf-8')
    p = re.compile('\'cdas\',[0-9],\'[0-9]*\'')
    num = int(p.search(html).group()[10:-1])
    url = "https://www.mdbg.net/chinese/rsc/img/stroke_anim/{}.gif".format(num)
    urlretrieve(url, self.sign + ".gif")


class MyHTMLParser(HTMLParser):
  word_depth = 0
  depth = 1
  words = []
  in_defs, in_pinyin, pinyin_next = False, False, False
  defs = []

  def handle_starttag(self, tag, attrs):
    self.depth += 1

    if tag == "tr" and ("class", "row") in attrs:
      self.word_depth = self.depth
      self.words += [Word()]
      print("Found new word")

    if self.word_depth != 0 and self.depth == self.word_depth + 3 and tag == "a":
      try:
        onclick = list(filter(lambda x: x[0] == "onclick", attrs))[0][1]
        result = re.compile('.\|.*[0-9]').search(onclick).group()
        if result:
          sign, pinyin_code = tuple(result.split('|'))
          self.words[-1].sign = sign
          self.words[-1].pinyin_code = pinyin_code
          print("* Found sign and sound:", sign, pinyin_code)
      except:
        pass

    if self.word_depth != 0 and ("class", "defs") in attrs:
      self.in_defs = True

    if self.word_depth != 0 and ("class", "pinyin") in attrs:
      self.in_pinyin = True
    if self.word_depth != 0 and self.in_pinyin and tag == "span":
      self.pinyin_next = True


  def handle_endtag(self, tag):
    if self.depth == self.word_depth:
      self.word_depth = 0
      print()

    if self.in_defs and tag == "div":
      self.in_defs = False
      defs = [x.strip() for x in self.defs if x != "/"]
      self.defs = []

      self.words[-1].defs = defs
      print("* Found defs:", defs)

    self.depth -= 1

  def handle_data(self, data):
    if self.in_defs:
      self.defs += [data]
    if self.pinyin_next:
      print("* Found pinyin:", data)
      self.words[-1].pinyin = data.lower()
      self.pinyin_next = False
      self.in_pinyin = False


def run():
  sign = input("Enter search term (pinyin/hanzi): ")

  html = urlopen(get_url(sign)).read().decode('utf-8')
  parser = MyHTMLParser()
  parser.feed(html)
  words = parser.words

  selected = -1
  while not selected in range(len(words)):
    print("Which definition did you mean?")
    for i, word in enumerate(words):
      print(str(i + 1) + ")", word.sign, word.pinyin, "-", "/".join(word.defs))
    selected = int(input("Enter number: ")) - 1

  words[selected].save_all()

if __name__ == "__main__":
  run()

