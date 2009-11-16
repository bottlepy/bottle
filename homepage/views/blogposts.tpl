%include header title="Blog Posts"
<h1>Blog Posts</h1>
This is a complete list of all blog posts since {{posts[-1][0]}} in chronological order.
<ul>
%for post in posts:
  %name = post[1].rsplit('/',1)[1].split('.',1)[0]
  %title = name.replace('blog_','').replace('_',' ').title()
  <li><a href="/page/{{name}}">{{title}}</a> - {{post[0]}}</li>
%end
</ul>
%include footer
