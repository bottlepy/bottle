$(document).ready(function() {
  var peak = 20; // Number of visible pixels

  var hPos = function(pos) {
    var dsize = $(document).height();
    var wsize = $(window).height();
    return Math.round(wsize*(pos/dsize))
  }

  var timeoutId;

  $('h1 > a.headerlink, h2 > a.headerlink').each(function(index){
    var lnk = $(this);
    var pos = lnk.offset().top
    var title = lnk.parent().text().replace('¶','')
    var node = $('<div>')
               .addClass('sidelegend')
               .css('top', hPos(pos)+'px')
               .appendTo('body')
    node.append($('<a>').text(title).attr('href', lnk.attr('href')))
    node.css('right', '-'+(node.outerWidth()-peak)+'px')
    node.mouseenter(function(){
      if(timeoutId) {
          window.clearTimeout(timeoutId);
          timeoutId = null;
      }
      $('div.sidelegend').animate({'right': '0px'}, 250)
    })
    node.mouseleave(function(){
      timeoutId = window.setTimeout(function(){
        $('div.sidelegend').each(function(){
          var n = $(this)
          n.animate({'right': '-'+(n.outerWidth()-peak)+'px'}, 250)
        })
        timeoutId = null;
      }, 1000)
    })

    $(document).resize(function(){
      var dsize = $(document).height();
      var wsize = $(window).height();
      node.css('top', hPos(pos)+'px')
    })

    $(window).resize(function(){
      var dsize = $(document).height();
      var wsize = $(window).height();
      node.css('top', hPos(pos)+'px')
    })
  })
})
