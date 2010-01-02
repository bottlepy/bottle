# Selector: jQuery plugin

I just wrote my first [jQuery](http://jquery.com/) plugin. It allows a user to visually select an area on the screen. Check out the demo:

<script src="http://github.com/defnull/Lucullus/raw/master/lucullus/data/static_files/js/jquery.selector.js" type="text/javascript"></script>
<p>
  <button id='selector_test'>Start Demo</button>
  <span id='selector_position' style='font-weight:bold; padding-left: 15px;'>Klick it! I know you want to!</span>
</p>
<script type="text/javascript">
  /*<![CDATA[*/
	var update = function(sa) {
			$('#selector_position')
			.text('x:'+sa.area[0]+' y:'+sa.area[1]+' width:'+(sa.area[2]-sa.area[0])+'px height:'+(sa.area[3]-sa.area[1]+'px'))
	}
	$('#selector_test').bind('click', function() {
		jQuery.selectArea(update, {onchange: update});
	});
  /*]]>*/
</script>

You can get the script [here](http://github.com/defnull/Lucullus/blob/master/lucullus/data/static_files/js/jquery.selector.js).
