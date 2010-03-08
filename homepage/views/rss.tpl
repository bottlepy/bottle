<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Bottle WSGI Blog Posts</title>
    <description>The latest Blog Posts</description>
    <link>http://bottle.paws.de/blog</link>
    %for post in posts:
      %link = 'http://bottle.paws.de/page/%s' % post.name
      <item>
        <title>{{post.title}}</title>
        <link>{{link}}</link>
        <guid isPermaLink="true">{{link}}</guid>
        <pubDate>{{post.blogtime.strftime('%a, %d %b %Y %H:%M:%S +0000')}}</pubDate>
        <description>{{post.preview.encode('utf8')}}</description>
      </item>
    %end
  </channel>
</rss>
