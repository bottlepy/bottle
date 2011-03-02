// Awesome scrollbar navigaion

POI = function(anchor, title, options) {
    // Create a Point-Of-Interest, a named position within the document.
    // @param anchor is the point of interest (HTML or jquery node). This MUST
    //        have an ID attribute.
    // @param title is the name of the POI (string)
    POI.all.push(this);
    
    //: Number of pixels the handle should be visible
    options = options || {};
    this.peak = options.peak || POI.peak;
    this.delay = options.delay || POI.delay;
    this.css = options.css || POI.css;

    this.pinned = false;
    this.visible = false;
    this.hide_timeout = null;

    this.anchor = $(anchor);
    this.id = this.anchor.attr('id');
    this.title = title || $(anchor).text();
    this.node  = $('<div>').addClass(this.css).appendTo('body');
    this.link  = $('<a>').text(this.title)
                         .attr('href', '#'+this.id)
                         .appendTo(this.node);
    this.node.css('right', '-'+(this.node.outerWidth()-this.peak)+'px');
    this.refresh();
    this.node.mouseenter(function() { POI.show(); });
    this.node.mouseleave(function() { POI.hide(POI.delay); });
}

POI.prototype.refresh = function() {
    // Re-arrange the anchors
    var dsize = $(document).height();
    var wsize = $(window).height();
    var pos = this.anchor.offset().top;
    var hpos = Math.round(wsize*(pos/dsize));
    this.node.css('top', hpos+'px');
}

POI.prototype.show = function() {
    // Show the handle
    if(this.visible) return;
    this.node.stop(true).animate({'right': '0px'}, 250);
    this.visible = true;
}

POI.prototype.hide = function() {
    // Hide the handle
    if(this.pinned) return;
    if(! this.visible) return;
    this.node.stop(true).animate({
        'right': '-'+(this.node.outerWidth()-this.peak)+'px'
    }, 250);
    this.visible = false;
}



// Static attributes and methods.

POI.all = Array();
POI.peak = 20;
POI.delay = 2000;
POI.css = 'sidelegend';
POI.hide_timeout = null;

POI.refresh = function() {
    // Refresh all at once
    jQuery.each(POI.all, function() {
        this.refresh();
    })
}

POI.show = function() {
    // Show all at once
    if(POI.hide_timeout) window.clearTimeout(POI.hide_timeout);
    POI.hide_timeout = null;
    jQuery.each(POI.all, function() {
        this.show();
    })
}

POI.hide = function(delay) {
    // Hide all at once after a specific delay
    if(POI.hide_timeout) window.clearTimeout(POI.hide_timeout);
    if(delay) {
        POI.hide_timeout = window.setTimeout(function() {
            POI.hide_timeout = null;
            POI.hide();
        }, delay)
    } else {
        jQuery.each(POI.all, function() {
            this.hide();
        })
    }
}

POI.whereami = function() {
    // Show and pin the currently viewed POI
    var position = $(window).scrollTop() + $(window).height() / 2;
    var last = null;
    jQuery.each(POI.all, function() {
        if(position < this.anchor.offset().top) return false;
        last = this;
    })
    if(last) {
        last.pinned = true;
        last.show();
    }
    jQuery.each(POI.all, function() {
        if(this != last) {
            this.pinned = false;
            this.hide();
        }
    })
}



$(document).resize(POI.refresh);
$(window).resize(POI.refresh);
$(window).scroll(POI.whereami);

// Global events that affect all POIs
$(document).ready(function() {
    $('.section > h1 > a.headerlink, .section > h2 > a.headerlink').each(function(index){
        var lnk = $(this);
        var title = lnk.parent().text().replace('¶','')
        var anchor = lnk.parent().parent()
        new POI(anchor, title)
    })
    POI.whereami();
})


