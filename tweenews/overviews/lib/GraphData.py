import scipy.io as sio
import numpy as np
import math
import codecs
from scipy.sparse import coo_matrix, hstack, csr_matrix
from utility import get_ticks, parse_date


def drawLineDist(cluster_num, start_time, end_time, mu, sigma):
    colors = ["#DEB887", "#A9A9A9", "#E9967A", "#00BFFF", "#333333", "#8FBC8F",
                       "#00ff00", "#b6fcd5", "#31698a", "#ff00ff", "#7fffd4", "#800000", "#8a2be2"]

    start_tick = get_ticks(parse_date(start_time))-3600*24*2
    end_tick = get_ticks(parse_date(end_time))+3600*24*2
    iter_count = 1700
    iter_step = (end_tick - start_tick) / iter_count

    line_num = cluster_num

    result_str = '\n\
\n\
<script type="text/javascript">\n\
var data = [];\n\
\n\
getData();\n\
var margin = {\n\
        top: 20,\n\
        right: 20,\n\
        bottom: 30,\n\
        left: 50\n\
    },\n\
    width = 520 - margin.left - margin.right,\n\
    height = 300 - margin.top - margin.bottom;\n\
\n\
var x = d3.scale.linear()\n\
    .range([0, width]);\n\
\n\
var y = d3.scale.linear()\n\
    .range([height, 0]),\n\
    yMap = function(d){\n\
        return null\n\
    }\n\
\n\
var format = d3.time.format("%Y%m%d");\nvar dateMin = format.parse("'
    result_str+=start_time
    result_str+='");\nvar dateMax = format.parse("'
    result_str+=end_time
    result_str+='");\n\
\n\
var xValue = function (v) {\n\
    var myDate = new Date( v.x *1000);\n\
    return myDate.toGMTString()\n\
},\n\
xScale = d3.time.scale().domain([dateMin, dateMax]).range([0, width]), // value -> display\n\
    xMap = function (d) {\n\
        return xScale(xValue(d));\n\
    }, // data -> display\n\
    xAxis = d3.svg.axis()\n\
    .scale(xScale)\n\
    .orient("bottom");\n\
\n\
var yAxis = d3.svg.axis()\n\
    .scale(y)\n\
    .orient("left")\n\
    .ticks(5);\n\
var svg = d3.select("#area2").append("svg")\n\
    .attr("width", width + margin.left + margin.right)\n\
    .attr("height", height + margin.top + margin.bottom)\n\
    .append("g")\n\
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");\n\
\n\
x.domain(['
    result_str+=str(start_tick)+','+str(end_tick)+']);\n'


    result_str+='y.domain([0, maxV])\n'

    for i in xrange(line_num):
        result_str+='\nvar line'+str(i+1)+'= d3.svg.line()\n\
        .x(function(d) {\n\
            return x(d.q);\n\
        })\n\
        .y(function(d) {\n\
            return y(d.l'+str(i+1)+');\n\
        });'
    result_str+='svg.append("g")\n\
    .attr("class", "x axis")\n\
    // .attr("transform", "translate(0," + height + ")")\n\
    .attr("transform", "translate(0," + height + ")")\n\
    .call(xAxis);\n\
\n\
svg.append("g")\n\
    .attr("class", "y axis")\n\
    // .attr("transform", "translate(0," + height + ")")\n\
    .call(yAxis);\n\n'
    for i in xrange(line_num):
        result_str+='svg.append("path")\n\
    .datum(data)\n\
    .attr("class", "line")\n\
    .attr("d", line'+str(i+1)+')\n\
    .style("stroke","'+colors[i]+'");\n\n'
    result_str+='function getData() {\n\
        maxV = 0\nfor (var i = 0; i<'+str(iter_count)+';i++){\nq='+str(start_tick)+'+i*'+str(iter_step)+'\n'

    for i in xrange(line_num):
        result_str+='l'+str(i+1)+'=gaussian(q, '+str(mu[i])+','+str(sigma[i])+')\n'

    result_str+='maxV = Math.max(maxV '
    for i in xrange(line_num):
        result_str+= ', l'+str(i+1)
    result_str+=')\nel={"q":q, '
    
    for i in xrange(line_num):
        result_str+='"l'+str(i+1)+'":l'+str(i+1)+","
    result_str += '}\ndata.push(el)};\n\
data.sort(function(x, y) {\n\
            return x.q - y.q;\n\
        }); \n\
}\n\
function gaussian(x, mean, sigma) {\n\
    var gaussianConstant = 1 / Math.sqrt(2 * Math.PI),\n\
        // mean =  1419305576,\n\
        // sigma = 39603.2746308182;\n\
\n\
    x = (x - mean) / sigma;\n\
    return gaussianConstant * Math.exp(-.5 * x * x) / sigma;\n\
};\n\
</script>\n\
'
    return result_str


class EntityGraphData():

    def __init__(self, termCount, termDic, termTypeDic, nodes, edges):
        self.termCount = termCount
        self.termDic = termDic
        self.termTypeDic = termTypeDic
        self.nodes = nodes
        self.edges = edges

    def __init__(self, threshold, event_num, cluster_num, reverse_voc, Pp_z, Pl_z, Po_z, Xaspects_list, aspect_Pp_z, aspect_Pl_z, aspect_Po_z):
        self.colors = ["#DEB887", "#A9A9A9", "#E9967A", "#00BFFF", "#333333", "#8FBC8F",
                       "#00ff00", "#b6fcd5", "#31698a", "#ff00ff", "#7fffd4", "#800000", "#8a2be2"]
        self.colors = list(self.colors)
        self.termtypeDic = {}
        self.termDic = {}
        self.termWeight = {}
        self.aspect_num = aspect_Pp_z.shape[1]

        self.eachTermWeight={}
        self.eachNodes={}
        for j in xrange(self.aspect_num):
            self.eachTermWeight[j]={}
            self.eachNodes[j] = set()

        termsp, termsl, termso = reverse_voc[
            'person'], reverse_voc['place'], reverse_voc['org']
        self.termCount = np.size(termsp) + np.size(termso) + np.size(termsl)

        termspW, termslW, termsoW = Pp_z[:, event_num], Pl_z[
            :, event_num], Po_z[:, event_num]

        ordered_ind = termspW.argsort()[::-1][:10]

        self.termWeight = {}

        for i in xrange(self.termCount):
            if i < np.size(termsp):
                self.termDic[i] = termsp[i].strip()
                self.termtypeDic[i] = "#9400D3"
                self.termWeight[i] = float(termspW[i])
                for j in xrange(self.aspect_num):
                    self.eachTermWeight[j][i] = float(aspect_Pp_z[i][j])
            elif i < np.size(termsl) + np.size(termsp):
                self.termDic[i] = termsl[i - np.size(termsp)].strip()
                self.termtypeDic[i] = "#228B22"
                self.termWeight[i] = float(termslW[i - np.size(termsp)])
                for j in xrange(self.aspect_num):
                    self.eachTermWeight[j][i] = float(aspect_Pl_z[i-np.size(termsp)][j])
            else:
                self.termDic[i] = termso[
                    i - np.size(termsp) - np.size(termsl)].strip()
                self.termtypeDic[i] = "#0000FF"
                self.termWeight[i] = float(
                    termsoW[i - np.size(termsp) - np.size(termsl)])
                for j in xrange(self.aspect_num):
                    self.eachTermWeight[j][i] = float(aspect_Po_z[i-np.size(termsp)-np.size(termsl)][j])
        self.nodes = set()
        self.edges = {}

        for topicType in xrange(cluster_num):
            Xs = Xaspects_list[topicType]
            Xp, Xl, Xo = Xs[1], Xs[2], Xs[3]
            Xall = hstack([Xp, Xl, Xo])

            # print Xp.shape
            erelation = np.dot(Xall.T, Xall)

            # print erelation.shape

            rows, cols = erelation.nonzero()
            for row, col in zip(rows, cols):
                if row == col:
                    continue
                else:
                    # if erelation[row,col]>threshold:
                    # print self.termDic[row], self.termWeight[row],
                    # self.termDic[col],self.termWeight[col],
                    # erelation[row,col]
                    if self.termWeight[row] > 0.04 and self.termWeight[col] > 0.04 and erelation[row, col] > threshold:
                        if (col, row, topicType) in self.edges:
                            continue
                        # print 'haha'
                        self.nodes.add(row)
                        self.nodes.add(col)
                        self.edges[(row, col, topicType)] = (
                            erelation[row, col])
                        self.eachNodes[topicType].add(row)
                        self.eachNodes[topicType].add(col)


        self.reorderDic = {}
        nodesList = list(self.nodes)
        self.eachReorderDic = {}
        for i in xrange(len(nodesList)):
            self.reorderDic[nodesList[i]] = i
        for i in xrange(cluster_num):
            self.eachReorderDic[i]={}
            nodesList = list(self.eachNodes[i])
            for j in xrange(len(nodesList)):
                self.eachReorderDic[i][nodesList[j]] = j



def aspectTextGen(gd, aspect):
    f = open('./media/entityGraphAppends.html')
    graphAppendsStr = f.read()
    f.close()

    return aspectDataTextGen(gd, aspect)+'\n'+graphAppendsStr

def aspectDataTextGen(gd, aspect):

    nodes = gd.eachNodes[aspect]
    edges = gd.edges
    to_write = "$(function() {var data = {\n\t\t\"nodes\":  [\n"

    for node in nodes:
        to_write+=aspectNodeTextGen(gd, node, aspect)
    to_write+= "],\n\"links\": [\n"

    for k, v in edges.iteritems():
        if k[2]!=aspect:
            continue
        else:
            to_write+= aspectLinkTextGen(gd, k,v, aspect)
    to_write+="]\n};"
    return to_write

def aspectLinkTextGen(gd, node_pair, value, topic):
    return "{\"source\": "+str(gd.eachReorderDic[topic][node_pair[0]])+", \"target\": "+str(gd.eachReorderDic[topic][node_pair[1]])+", color:\""+gd.colors[node_pair[2]]+"\", "+"weight:"+str(getPathWidth(value))+" },\n"

def aspectNodeTextGen(gd, node, topic):
    # print node
    return "{\"id\": "+str(gd.eachReorderDic[topic][node])+", \"name\": \""+gd.termDic[node]+"\", size:\""+str(getNodeSize(gd.eachTermWeight[topic][node]))+"\",color:\""+gd.termtypeDic[node]+"\"},\n"


def textGen(gd):
    f = open('./media/entityGraphAppends.html')
    graphAppendsStr = f.read()
    f.close()
    return dataTextGen(gd)+'\n'+graphAppendsStr

def dataTextGen(gd):
    nodes = gd.nodes
    edges = gd.edges
    to_write = "$(function() {var data = {\n\t\t\"nodes\":  [\n"
    for node in nodes:
        to_write += nodeTextGen(gd, node)
    to_write += "],\n\"links\": [\n"

    for k, v in edges.iteritems():

        to_write += linkTextGen(gd, k, v)
    to_write += "]\n};"
    return to_write


def getNodeSize(value):
    if value==0:
        return 1
    s = math.log(value * 10 ** 4)
    return s
    # return 5


def getPathWidth(value):
    # value = math.log(value)
    return math.log(value * 4)


def nodeTextGen(gd, node):
    return "{\"id\": " + str(gd.reorderDic[node]) + ", \"name\": \"" + gd.termDic[node] + "\", size:\"" + str(getNodeSize(gd.termWeight[node])) + "\",color:\"" + gd.termtypeDic[node] + "\"},\n"


def linkTextGen(gd, node_pair, value):

    return "{\"source\": " + str(gd.reorderDic[node_pair[0]]) + ", \"target\": " + str(gd.reorderDic[node_pair[1]]) + ", color:\"" + gd.colors[node_pair[2]] + "\", " + "weight:" + str(getPathWidth(value)) + " },\n"

def drawWordCloud(word_distribution):
    result_str = 'data = [\n'

    for k, v in word_distribution.iteritems():
        if v*10000<=40:
            continue
        result_str+='{"name":"'+k+'","size":'+str( wordCloudSize(v*10000))+'},'
    result_str+=']\n'
    text_after = '  var fill = d3.scale.category20();\n\
  d3.layout.cloud().size([300, 300])\n\
      .words(data.map(function(d) {\n\
        return {text: d.name, size: d.size};\n\
      }))\n\
      .padding(5)\n\
      .rotate(function() { return ~~(Math.random() * 2) * 90; })\n\
      .font("Impact")\n\
      .fontSize(function(d) { return d.size; })\n\
      .on("end", draw)\n\
      .start();\n\
  function draw(words) {\n\
    d3.select("placeholder").append("svg")\n\
        .attr("width", 300)\n\
        .attr("height", 300)\n\
      .append("g")\n\
        .attr("transform", "translate(150,150)")\n\
      .selectAll("text")\n\
        .data(words)\n\
      .enter().append("text")\n\
        .style("font-size", function(d) { return d.size + "px"; })\n\
        .style("font-family", "Impact")\n\
        .style("fill", function(d, i) { return fill(i); })\n\
        .attr("text-anchor", "middle")\n\
        .attr("transform", function(d) {\n\
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";\n\
        })\n\
        .text(function(d) { return d.text; });\n\
  }'
    result_str+=text_after
    return result_str

def wordCloudSize(value):
    value = float(value)

    return (value - 40)/float(310-40)*(50-10)+10
    



if __name__ == '__main__':

    # gD = EntityGraphData(0.5, 2)

    print drawWordCloud({'adf':500, 'asdffff':20,'asdfdddd':10  })

