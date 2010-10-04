"""Stemming"""
import sys
import os
import re
import string

__version__ = "1.0"
__authors__ = "Brittany Thompson <miller317@gmail.com>"
__date__ = "Oct 1, 2010"

"""
Used algorithm from
"An algorithm for suffix stripping" by M.F.Porter 1980
http://tartarus.org/~martin/PorterStemmer/def.txt
Along with code segments from Vivake Gupta January 2001
http://tartarus.org/~martin/PorterStemmer/python.txt
"""
class Stemming:
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        
        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def ends(self, s): #written by Vivake Gupta http://tartarus.org/~martin/PorterStemmer/python.txt
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def m(self): #written by Vivake Gupta http://tartarus.org/~martin/PorterStemmer/python.txt
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        print "in m"
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1
        print "in m"

    def remove(self, a):
        self.k = self.k - 1

    def append(self, c):
        self.b = self.b[:self.j+1] + c + self.b[self.j+len(c)+1:]

    def isNotVowel(c):
        if c=='a' or c=='e' or c=='i' or c=='o' or c=='u':
            return 0

    def step1(self):
        if self.ends('sses'): #sses -> ss
            self.remove(2)
        elif self.ends('ies'): #ies -> i 
            self.remove(2)
        elif self.ends('s'): #s ->  
            self.remove(1)
        elif self.m>0 and self.ends('eed'): #eed -> ee
            self.remove(1)
        elif self.ends('ed'): #ed ->
            if self.k > 4:
                self.remove(2) 
                self.step1_2()
        elif self.ends('ing'): #ing ->
            if self.k > 4:
                self.remove(3)
                self.step1_2()
        if self.ends('y') and self.k>3: #y -> i
            self.remove(1)
            self.append('i')
        return self

    def step1_2(self):
        if self.ends('at'): #at -> ate
            self.append('e')
        elif self.ends('bl'): #bl -> ble
            self.append('e')
        elif self.ends('iz'): #iz -> ize
            self.append('e')
        elif self.k ==  self.k-1: #remove double letters at end
            if self.ends('ll') or self.ends('ss') or self.ends('zz'):
                return word
            else:
                self.remove(1)
        return self

    def step2(self):
        if self.ends('ational'):  #ational -> ate
            self.remove(5)
            self.append('e')
        elif self.ends('tional'): #tional -> tion
            self.remove(2)
        elif self.ends('enci'): #enci -> ence
            self.remove(1)
            self.append('e')
        elif self.ends('anci'): #anci -> ance
            self.remove(1)
            self.append('e')
        elif self.ends('izer'): #izer -> ize
            self.remove(1)
        elif self.ends('abli'): #abli -> able
            self.remove(1)
            self.append('e')
        elif self.ends('alli'): #alli -> al
            self.remove(2)
        elif self.ends('entli'): #entli -> ent
            self.remove(2)
        elif self.ends('eli'): #eli -> e
            self.remove(2)
        elif self.ends('ousli'): #ousli -> ous
            self.remove(2)
        elif self.ends('ization'): #ization -> ize
            self.remove(5)
            self.append('e')
        elif self.ends('ation'): #ation -> ate
            self.remove(3)
            self.append('e')
        elif self.ends('ator'): #ator -> ate
            self.remove(2)
            self.append('e')
        elif self.ends('alism'): #alism -> al
            self.remove(3)
        elif self.ends('iveness'): #iveness -> ive
            self.remove(4)
        elif self.ends('fulness'): #fulness -> ful
            self.remove(4)
        elif self.ends('ousness'): #ousness -> ous
            self.remove(4)
        elif self.ends('aliti'): #aliti -> al
            self.remove(3)
        elif self.ends('iviti'): #iviti -> ive
            self.remove(3)
            self.append('e')
        elif self.ends('biliti'): #biliti ->ble
            self.remove(5)
            self.append('le')
        return self

    def step3(self): #m>0
        if self.ends('icate'): #icate -> ic
            self.remove(3)
        elif self.ends('ative'): #ative ->
            self.remove(5)
        elif self.ends('alize'): #alize -> al
            self.remove(3)
        elif self.ends('iciti'): #iciti -> ic
            self.remove(3)
        elif self.ends('ical'): #ical -> ic
            self.remove(2)
        elif self.ends('ful'): #ful ->
            self.remove(3)
        elif self.ends('ness'): #ness ->
            self.remove(4)
        return self

    def step4(self):#m>1
        if self.ends('al'): #al ->
            self.remove(2)
        elif self.ends('ance'): #ance ->
            self.remove(4)
        elif self.ends('ence'): #ence ->
            self.remove(4)
        elif self.ends('er'): #er ->
            self.remove(2)
        elif self.ends('ic'): #ic ->
            self.remove(2)
        elif self.ends('able'): #able ->
            self.remove(4)
        elif self.ends('ible'): #ible ->
            self.remove(4)
        elif self.ends('ant'): #ant ->
            self.remove(3)
        elif self.ends('ement'): #ement ->
            self.remove(5)
        elif self.ends('ment'): #ment ->
            self.remove(4)
        elif self.ends('ent'): #ent->
            self.remove(3)
        elif self.ends('tion'): #tion -> t
            self.remove(3)
        elif self.ends('sion'): #sion -> s
            self.remove(3)
        elif self.ends('ou'): #ou ->
            self.remove(2)
        elif self.ends('ism'): #ism ->
            self.remove(3)
        elif self.ends('ate'): #ate ->
            self.remove(3)
        elif self.ends('iti'): #iti ->
            self.remove(3)
        elif self.ends('ous'): #ous ->
            self.remove(3)
        elif self.ends('ive'): #ive ->
            self.remove(3)
        elif self.ends('ize'): #ize ->
            self.remove(3)
        return self

    def step5(self): #m>1
        if self.ends('e'): #e ->
            self.remove(1)
        elif self.ends('dd'): #dd -> d
            self.remove(1)
        elif self.ends('ll'): #ll -> l
            self.remove(1)
        return self

    def stem_words(self, p, i, j):
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()

        return self.b[self.k0:self.k+1]



if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="Stemming",
                                   usage="usage: %prog [options] <textfile>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-i', '--input', help="Input stored files [default: %default]", default=os.path.join(_storage, 'stopped', ''))
    parser.add_option('-o', '--output', help="Output location to stored files [default: %default]", default=os.path.join(_storage, 'stemmed', ''))

    (options, args) = parser.parse_args()
    p = Stemming()
    if args:
        for arg in args:
            if os.path.isfile(arg):
                fp = open(args[0], "r")
                while 1:
                    output = ''
                    word = ''
                    line = fp.readline()
                    if line == '':
                        break
                    for c in line:
                        if c.isalpha():
                            word += c.lower()
                        else:
                            if word:
                                output += p.stem_words(word, 0,len(word)-1)
                                word = ''
                                output += c.lower()
                    print output,

                fp.close()
    else:
        indir=options.input
        outdir=options.output
        verbose=options.verbose
        if indir:
            for f in os.listdir(indir):
                print f
                if verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                output = ''
                while 1:
                    word = ''
                    line = fp.readline()
                    if line == '':
                        break
                    for c in line:
                        if c.isalpha():
                            word += c.lower()
                        else:
                            if word:
                                output += p.stem_words(word, 0,len(word)-1)
                                word = ''
                                output += c.lower()
                    print output
                fp.close()
                if outdir:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(output)
                    fp.close()

