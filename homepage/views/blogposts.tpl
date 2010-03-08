%rebase basehtml title="Blog Posts"
%from cgi import escape
<h1>Blog Posts</h1>
This is a complete list of all blog posts since {{posts[-1].blogtime.strftime('%A, %d %B %Y')}} in chronological order.
%for post in posts:
  <h3><a href="/page/{{post.name}}">{{post.title}}</a></h3>
  <strong>{{post.blogtime.strftime('%A, %d %B %Y')}}</strong>
  <p>{{!post.preview.encode('utf-8')}} <a href="/page/{{post.name}}">...</a></p>
%end

