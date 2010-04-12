%title = globals().get('title', 'Homepage')
%import bottle
%version = bottle.__version__
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>{{title}} - Bottle: Python Web Framework</title>
    <link type="text/css" rel="stylesheet" href="/main.css" />
    <link type="text/css" rel="stylesheet" href="/pygments.css" />
    <link rel="alternate" type="application/rss+xml"  href="/rss.xml" title="Changed Pages">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" >
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js" type="text/javascript"></script>
  </head>
  <body>
    <div id="navigation">
      <h1>Navigation</h1>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/page/docs">Documentation (stable)</a></li>
        <li><a href="/docs/">Documentation (testing)</a></li>
        <li><a href="/page/faq">F.A.Q.</a></li>
        <li><a href="/blog">Blog</a></li>
        <li><a href="/page/contact">Contact</a></li>
      </ul>
      <h1>Links</h1>
      <ul>
        <li><a target="_blank" href="http://pypi.python.org/pypi/bottle">Download</a></li>
        <li><a target="_blank" href="http://github.com/defnull/bottle">GitHub Repository</a></li>
        <li><a target="_blank" href="http://github.com/defnull/bottle/issues">Issue Tracker</a></li>
        <li><a target="_blank" href="http://groups.google.de/group/bottlepy">Google Groups</a></li>
        <li><a target="_blank" href="http://twitter.com/bottlepy">Twitter</a></li>
      </ul>
      <h1>Other</h1>
      <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
        <input type="hidden" name="cmd" value="_s-xclick">
        <input type="hidden" name="hosted_button_id" value="10013866">
        <input type="image" src="https://www.paypal.com/en_US/i/btn/btn_donate_SM.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
        <img alt="" border="0" src="https://www.paypal.com/de_DE/i/scr/pixel.gif" width="1" height="1">
      </form>
    </div>

    %include

    <div id='footer'>
      <div>Powered by <a href="/"><img src="/bottle-sig.png" /></a> <small>(Version {{version}})</small></div>
      <div>Browse sources at <a href="http://github.com/defnull/bottle">GitHub</a></div>
    </div>
  </body>
</html>
