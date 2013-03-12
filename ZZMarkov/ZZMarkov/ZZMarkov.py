import re
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import time

from threading import Lock
from tornado.options import define, options

define("port", default=8889, help="run on the given port", type=int)

class ZZLink:
    def __init__(self, fromNode, toNode, dimension = 1):
        self.fromNode = fromNode
        self.toNode = toNode
        self.dimension = dimension
        self.strength = 1

    def getTo(self):
        return self.toNode

    def getFrom(self):
        return self.fromNode

    def getStrength(self):
        return self.strength

    def CompareTo(self, other):
        if self.strength > other.strength:
            return 1
        if self.strength < other.strength:
            return -1
        if self.strength == other.strength:
            return 0

    def Equals(self, other):
        return self.fromNode.Equals(other.fromNode) and self.toNode.Equals(other.toNode)

class ZZNode:
    def __init__(self, data):
        self.data = data
        self.backLinks = []
        self.nextLinks = []
        self.sideLinks = []

    def getData(self):
        return self.data

    def Equals(self, other):
        return self.data == other.data

    def AddBackLink(self, backLink):
        for link in self.backLinks:
            if link.Equals(backLink):
                link.strength += 1
                return
        self.backLinks.append(backLink)

    def AddNextLink(self, nextLink):
        for link in self.nextLinks:
            if link.Equals(nextLink):
                link.strength += 1
                return
        self.nextLinks.append(nextLink)

    def AddSideLink(self, sideLink):
        for link in self.sideLinks:
            if link.Equals(sideLink):
                link.strength += 1
                return
        self.sideLinks.append(sideLink)

    def GetStrongestBackLink(self):
        ret = False
        strongest = -1024
        for link in self.backLinks:
            if link.strength > strongest:
                strongest = link.strength
                ret = link
        return ret

    def GetStrongestNextLink(self):
        ret = False
        strongest = -1024
        for link in self.nextLinks:
            if link.strength > strongest:
                strongest = link.strength
                ret = link
        return ret

    def GetStrongestSideLink(self):
        ret = False
        strongest = -1024
        for link in self.sideLinks:
            if link.strength > strongest:
                strongest = link.strength
                ret = link
        return ret

    def GetSideLinkStrength(self):
        strongest = 0
        for link in self.sideLinks:
            strongest += link.strength
        return strongest

class ZZStructure:
    def __init__(self):
        self.lines = []
        self.wordList = []
        self.lastSentence = []
        self.sentenceNode = False
        self.wordNode = False

        self.filter = re.compile(r'[^0-9^a-z^A-Z^\s]+')
        
        self.wordList.append(ZZNode(""))

    def GetNodeForData(self, data):
        for node in self.wordList:
            if node.getData() == data:
                return node
        node = ZZNode(data)
        self.wordList.append(node)
        return node

    def GetNodeForSentence(self, data):
        for node in self.lines:
            if node.getData() == data:
                return node
        node = ZZNode(data)
        self.wordList.append(node)
        return node

    def AddSentence(self, sentence):
        sentence = sentence.replace("\r", "").replace("\n", "").replace("\t", "")
        sentence = self.filter.sub(" ", sentence)
        words = sentence.split(" ")
        if len(words) == 0:
            return ""
        nodes = []
        for data in words:
            if data != "" and data != " ":
                nodes.append(self.GetNodeForData(data))
        
        temp = self.GetNodeForSentence(words)
        if self.sentenceNode != False:
            temp.AddNextLink(ZZLink(temp, self.sentenceNode))
            self.sentenceNode.AddBackLink(ZZLink(temp, self.sentenceNode, 2))
        self.sentenceNode = temp

        for node in nodes:
            node.AddSideLink(ZZLink(node, self.sentenceNode, 2))

        nodes.insert(0, self.GetNodeForData(""))
        nodes.append(self.GetNodeForData(""))

        for x in range(0, len(nodes) - 1):
            nodes[x].AddNextLink(ZZLink(nodes[x], nodes[x + 1]))
            nodes[x + 1].AddBackLink(ZZLink(nodes[x], nodes[x + 1]))

    def GenerateSentence(self, input):
        input = input.replace("\r", "").replace("\n", "").replace("\t", "")
        input = self.filter.sub(" ", input)
        words = input.split(" ")
        if len(words) == 0:
            return ""
        nodes = []
        for data in words:
            if data != "" and data != " ":
                nodes.append(self.GetNodeForData(data))

        strongest = -1024
        popWord = False
        for node in nodes:
            if node.GetSideLinkStrength() > strongest and node.GetStrongestSideLink() != False:
                strongest = node.GetSideLinkStrength()
                popWord = node.GetStrongestSideLink().getTo()                

        if popWord != False:
            sideLink = popWord.GetStrongestNextLink()
            if sideLink != False:
                popWord = sideLink.getTo()

        if popWord != False:
            nodes = []
            for word in popWord.getData():
                nodes.append(self.GetNodeForData(word))

        sentence = []

        center = False
        strongest = -1024
        for node in nodes:
            if node.GetStrongestNextLink().getStrength() > strongest:
                strongest = node.GetStrongestNextLink().getStrength()
                center = node

        sentence.append(center)
        if center == False:
            return ""
        if center.GetStrongestNextLink() == False:
            return ""
        tempNode = center.GetStrongestNextLink().getTo()

        while tempNode.getData() != "" and tempNode not in sentence:
            sentence.append(tempNode)
            tempNode = tempNode.GetStrongestNextLink().getTo()

        tempNode = center.GetStrongestBackLink().getFrom()

        while tempNode.getData() != "" and tempNode not in sentence:
            sentence.insert(0, tempNode)
            tempNode = tempNode.GetStrongestBackLink().getFrom()

        ret = ""
        for word in sentence:
            ret += word.getData() + " "
        return ret

zz = ZZStructure()
zz.AddSentence("OpenBwall, not to be confused with openwall, is meant to be a blog and brain dump for bwall aka Brian Wallace.  It will also be a place for me to host any projects that have nothing to do with anything I am affiliated with.  I often find myself yelling from the mountains as Ballast Security when not all of Ballast Security agrees with me.  Being able to post to something that is just mine, just me, will be good for Ballast Security and me.  Also, I have wanted to dig more into non-security projects such as Artificial Intelligence. This blog, at times, might be about my personal life.  Sometimes, I want to vent about things, but have no proper location to actually vent about them.  In the past, I have found that venting to Artificial Intelligence tends to make it quite rude over time.  You haven't developed an angry AI until it calls you a cunt.")
zz.AddSentence("For my senior project(capstone for Software Engineers at RIT), my team and I are modifying open source software to integrate with a cloud computing service.  I am being vague, because the actual project is irrelevant to this post.  We recently were asked a question that we have not been able to come up with a good answer for yet.  That question is, \"How do you know when you are done?\"  So far, all we can say to that is, \"Its open source.\"  Open source projects tend to not have an end.  Why would they have an end?  Not like funding will run out.  Most open source projects stop when the developers don't care about it anymore, whether it has become too messy to continue coding or no one is really using it.  The problem is that with this particular project, and with our time limit, we don't really have enough time to just burn out on the project, and we need a definitive way to say we are done.  The best chance we have is to time box our development, and just try to make sure that any more features we add are stable around when we decide to stop developing.  That leaves us very open to risk, especially with testing.  It is very hard to predict how long bug fixes will take when you haven't even developed the code that could possibly have bugs in it.")
print "Done loading"



class HomeHandler(tornado.web.RequestHandler):
    def post(self, action):
        global zz
        if action == "submit":
            input = str(self.get_argument("input").encode('ascii', 'ignore'))
            for sentence in input.split("."):
                zz.AddSentence(sentence)
        if action == "query":
            input = str(self.get_argument("input").encode('ascii', 'ignore'))
            self.write(zz.GenerateSentence(input))

application = tornado.web.Application([
                                       (r"/api/markov/(.+)", HomeHandler),
                                       ])

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()         

if __name__ == "__main__":
    main()