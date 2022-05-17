#bætir við ner-tögum úr nafnaþekkjara í xml-skjölc
from os import listdir
from os.path import isfile, join, exists
from lxml import etree
from lxml.etree import Element as ET
from copy import deepcopy
from NERTag import NERTag
import timeit
from collections import OrderedDict

nerTag = NERTag()

texti = "Á upplýsingafundi almannavarna og landlæknis í gær gaf Þórólfur lítið upp varðandi hvaða afléttingar hann leggur til en sagði þó að í tillögum sínum væru tilslakanir í menntastofnunum og á skipulögðum menningarviðburðum. Þá væru einnig tillögur í minnisblaðinu sem snúa að áhorfendum á íþróttaviðburðum."
print(len(texti))

output = nerTag.tag_sentence(texti)

print(output)
