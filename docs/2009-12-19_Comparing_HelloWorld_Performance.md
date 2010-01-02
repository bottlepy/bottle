# Comparing "Hello World" Performance

I was curious and tested a "Hello World!" app with [Paste](http://pythonpaste.org/), [Fapws3](http://github.com/william-os4y/fapws3), [CherryPy](http://www.cherrypy.org/), [WSGIRef](http://www.wsgi.org/wsgi/) and the brand new [Tornado](http://www.tornadoweb.org/) adapter.

    #!Python
    @bottle.route('/')
    def index():
        return 'Hello World'
    bottle.run(server=...)

Some of you will now say "These tests are not representative. Real apps are much more complex." and you are right. This benchmark will not tell you how fast your real app can go, but it can tell you how much overhead you get with each of the available server adapters.

I used [ApacheBench](http://en.wikipedia.org/wiki/ApacheBench) on an old single core AMD3000+ over a GBit network connection. Each server adapter was tested with 10000 requests and the "concurrent request" settings (-c) set to 1, 10, 100 and 1000. Here are the results:

This chart shows simultaneous connections (x-axis) and mean requests per sec (y-axis)

<div id="ChartContainer" style="width:600px; height:400px;"></div>

As you can see, fapws3 performs *great*! But to be fair: fapws3 is the only tested server implemented in C. Tornado is the fastest pure python server in this test.

<script src="http://www.highcharts.com/js/highcharts.js" type="text/javascript"></script>
<!--[if IE]>
<script src="http://www.highcharts.com/js/excanvas-compressed.js" type="text/javascript"></script>
<![endif]-->

<script type="text/javascript">
   $(document).ready(function() {
var chart = new Highcharts.Chart({
   chart: { renderTo: 'ChartContainer', margin: [60, 150, 60, 60] },
   title: { text: 'Requests per Second' },
   subtitle: { text: 'Depending on Number of Simultaneous Connections' },
   xAxis: {
      title: { text: 'Connections' },
      categories: [1, 10, 100, 1000],
   },
   yAxis: { title: { text: 'Requests per Second' }, },
   tooltip: {
      formatter: function() {
                return '<b>'+ this.series.name +'</b><br/>'+
            this.x +': '+ this.y +'req/s';
      }
   },
   legend: {
      layout: 'vertical',
      style: {
         left: 'auto',
         bottom: 'auto',
         right: '10px',
         top: '100px'
      }
   },
   series: [
     {name: 'Fapws3',    data: [1707.94, 2058.70, 2070.98, 1960.06]},
     {name: 'Tornado', data: [1143.59, 1498.65, 1466.11, 1413.46]},
     {name: 'CherryPy', data: [1091.10, 1146.08, 1227.02, 731.12]},
     {name: 'WSGIRef', data: [608.66, 739.33, 611.85, 680.95]},
     {name: 'Paste', data: [518.35, 588.38, 570.65, 553.82]},
   ]
});
})
</script>

