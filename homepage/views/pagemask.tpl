%include header title=page.title.encode('utf-8')
<div id='mdpage'>
{{page.html.encode('utf-8')}}
</div>
<div style='text-align: right; color: #ddd'>
Last modified: - {{page.mtime}}
</div>
%include footer
