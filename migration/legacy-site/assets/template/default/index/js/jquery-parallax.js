$.fn.parallax = function ( resistance, mouse, num ) 
{
	$el = $( this );
	if(num==1){
		TweenLite.to( $el, 1, 
		{
			x : -(( mouse.clientX - (window.innerWidth/1.5) ) / resistance ),
			y : (( mouse.clientY - (window.innerHeight/1) ) / resistance )
		});
	}else{
		TweenLite.to( $el, 1, 
		{
			x : 0,
			y : 0
		});
	}
};