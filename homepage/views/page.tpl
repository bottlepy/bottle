%rebase basehtml title=page.title.encode('utf-8')
<div id='mdpage'>
{{!page.html.encode('utf-8')}}
</div>
<div style="text-align: left; color:grey;">Edit this page at <a href="http://github.com/defnull/bottle/blob/master/docs/{{page.name}}.md">GitHub</a></div>
%if page.is_blogpost:
<div style="text-align: left; color:grey;">Posted on {{page.blogtime.strftime('%A, %d %B %Y')}} by <a href="/page/contact">defnull</a>. Comments are not implemented.</div>
%end

