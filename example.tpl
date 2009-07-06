%header = 'Test Template'
<html>
  <head>
    <title>{{header.title()}}</title>
  </head>
  <body>
    <h1>{{header.title()}}</h1>
    <p>Items in list: {{len(items)}}</p>
    <ul>
    %for item in items:
      <li>
      %if isinstance(item, int):
        Zahl: {{item}}
      %else:
        %try:
        Other type: ({{type(item).__name__}}) {{repr(item)}}
        %except:
        Error: Item has no string representation.
        %end try-block (yes, you may add comments here)
      %end
      </li>
    %end
    </ul>
  </body>
</html>
