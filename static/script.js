$(function(){

	$('.preload').fadeOut(1000);

	$('.iq_close_cont').hide();
	$('.iq_close').click(function(){
		$('.iq_close_cont').fadeIn();
		$(this).fadeToggle();

	});

	$('.cancel').click(function(){
		$('.iq_close_cont').hide();
		$('.iq_close').fadeToggle();
		$(this).removeClass('on');
	});
	$('.exit').click(function(){
		 $('.preload').delay(1000).fadeIn(2000);
		 $(this).addClass('on');
         setTimeout(function() {
            window.location.href = '/';
        }, 3000);
	});



	$('.header .h_inner .list').click(function(){
		$(this).toggleClass('close');
		$('.menu_wrap').toggleClass('open').slideToggle();

	});

	$('.gnb li a').hover(function(){
		$(this).addClass('iq_txt_ani2');
	}, function(){
		$(this).removeClass('iq_txt_ani2');
	});

	
	$('.list_txt').hover(function(){
		$('.con1').addClass('show');
		$('.con_title').delay(500).slideDown();
	}, function(){
		$('.con1').removeClass('show');
		$('.con_title').slideUp();
	});
	

	$('.btn.progress').click(function(){
		$(this).addClass('on');
		$(this).addClass('onnext');
	});


	$('.btn_wrap.step a').click(function(){
		$('.iq_wrap_inner.progress_pic').addClass('start');
	});
	

	$('.hidelater').delay(3000).fadeOut(800, function(){
		$('.showlater').fadeIn(800, function(){
			$('.iq_wrap.icon').addClass('start');
		});

	});

	$('.btn_wrap.select .btn_select').click(function(){
		 $(this).addClass('on');
	});
	

	 $('.page1').click(function(){
		 $('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step01';
        }, 3000);
    });


/*
	$('.page2 a').click(function(){
		
		 $('.preload').delay(1000).fadeIn(1000);

		  setTimeout(function() {
            window.location.href = 'step02-0.html';
        }, 2000);
        
    });
*/
/*
	$('.page02-1').click(function(){
		 $('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step02-1.html';
        }, 3000);
    });
*/
	$('.page02-2').click(function(){
		 $('.preload').delay(1000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step02-2.html';
        }, 2000);
    });

	$('.page02-3').click(function(){
		
		 $('.preload').delay(2000).fadeIn(1000);

		  setTimeout(function() {
            window.location.href = 'step02-3.html';
        }, 3000);
        
    });
	$('.page02-4').click(function(){
		 $('.preload').delay(1000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step02-4.html';
        }, 2000);
    });



	$('.page3').click(function(){
		 $('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step03.html';
        }, 3000);
    });

	$('.page4').click(function(){
		$('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step04.html';
        }, 3000);
    });

	$('.page5').click(function(){
		$('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step05.html';
        }, 3000);
    });

	$('.page8 a').click(function(){
         setTimeout(function() {
            window.location.href = 'step08.html';
        }, 1000);
    });

	 $('.page6').click(function(){
		 $('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step06';
        }, 3000);
    });

	$('.page9').click(function(){
		$('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = 'step09';
        }, 3000);
    });

	 $('.index').click(function(){
		 $('.preload').delay(2000).fadeIn(1000);
         setTimeout(function() {
            window.location.href = '/';
        }, 3000);
    });


	$('.layer_pop .layer_pop_inner .close').click(function(){
		$('.layer_pop').fadeOut();
	});

	$('.gnb li a, .term li a').click(function(){
		event.preventDefault();
		$('.layer_pop').fadeIn();
		
		$('.layer_pop_inner .content').hide();
		$(this.hash).fadeIn();
		$('.header .h_inner .list').removeClass('close');
		$('.menu_wrap').removeClass('open').slideUp();

	});

	
	
	// 마지막 이미지 펼쳐지게
	/*
	var checkImg = $('.iq_result_back_inner div').length;

	for(i=1; i<=checkImg; i++){
		
		var ranNumx = Math.floor(Math.random() * 3000);
		var ranNumy = Math.floor(Math.random() * 3000);

		$('.iq_result_back_inner div').eq(i).css({ left:ranNumx, top:ranNumy });
	}

	$(document).on( "mousemove", function(event){

		event.pageX = event.pageX / 30;
		event.pageY = event.pageY / 30;


		document.getElementsByClassName('iq_result_back_inner div').style.transform = 'rotate(' + event.pageX + 'deg)';

		//$( "#log" ).text( "pageX: " + event.pageX + ", pageY: " + event.pageY );
	});
	*/

  $("#user_upload_input").change( function(e){
      var selectedFile = e.target.files[0];
      var reader = new FileReader();
      reader.onload = (function() {
        return function(e) {
          document.getElementById('user_upload_input').diabled = true;
          document.getElementById('user_upload_img').src = e.target.result;
          document.getElementById('uploading_button').style.display = 'block';
          uploadImage();
        };
      })();
      reader.readAsDataURL(selectedFile);
  })

});

function answer(step, ans) {
  $('.preload').delay(1000).fadeIn(1000);
  setTimeout(function() {
    window.location.href = '/step0'+step + 'a/'+ans;
  }, 2000);
}

function nextQuestion(step) {
  $('.preload').delay(2000).fadeIn(1000);
  setTimeout(function() {
      window.location.href = '/step0' + (step+1);
  }, 3000);
}

function uploadImage() {
  var XHR = new XMLHttpRequest();
  var FD = new FormData(document.getElementById('image_form'));
  XHR.addEventListener("load", function(event) {
    if (JSON.parse(event.target.responseText).r == 's') {
      console.log('image uploaded');
      window.location.href = '/step07';
      //user_image = JSON.parse(event.target.responseText).i;
      ////document.getElementById('stage4-image-599').src = '{{option.imageoriginal}}' + user_image + '.jpg';
      //setTimeout(function() {document.getElementById('stage3-sendbutton').hidden = false; stage(400);}, 0);
    } else {
      alert('이미지 전송에 실패했습니다. 다시 시도해 주세요.');
      //document.getElementById('stage3-sendbutton').hidden = false;
      document.getElementById('user_upload_input').diabled = false;
    }
  });
  XHR.addEventListener("error", function(event) {
    alert('이미지 전송에 실패했습니다. 다시 시도해 주세요.');
    //document.getElementById('stage3-sendbutton').hidden = false;
    document.getElementById('user_upload_input').diabled = false;
  });
  XHR.open("POST", "/image")
  XHR.send(FD);
  //stage(310);
}