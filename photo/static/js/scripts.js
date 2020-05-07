$(document).ready(function(){


  // Sidebar collapse 
  $('#sidebarCollapse').on('click', function () {
    $('#sidebar').toggleClass('active');
  });

  $('form input').change(function () {
    $('form p').text(this.files.length + " file(s) selected");
  });


  const $valueSpan = $('.valueSpan');
  const $values = $('.custom-range');
  $valueSpan.each(function(i, el){
    $(this).html($values[i].value);
  });

  $values.each(function(i, el) {
    $(this).on('input change', () => {
      $valueSpan[i].innerHTML = $(this).val();
      //$valueSpan[i].innerText = $(this).val();
    });
  });

  var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

  $("#sendDistort").on("click", () => {
    console.log("hello");
    let selectionImg = $("#selectedImg").get(0);
    if (selectionImg.src) {
      $.ajax({
        type: "get",
        url: "api/distort/"+selectionImg.alt,
        beforeSend: function (xhr) {
          xhr.overrideMimeType('text/plain; charset=x-user-defined');
        },
        data: {
          f:  $("#f").val(),
          k1: $("#k1").val(),
          k2: $("#k2").val(),
        },
        dataType: "text",
        success: function(response, status, jqXHR) {       
          if(response.length < 1){
              alert("The image was not received");
              $("#distortedImg").attr("src", "data:image/png;base64,");
              return
          }

          var binary = "";
          var responseText = jqXHR.responseText;
          var responseTextLen = responseText.length;

          for ( i = 0; i < responseTextLen; i++ ) {
              binary += String.fromCharCode(responseText.charCodeAt(i) & 255)
          }
          $("#distortedImg").attr("src", "data:image/png;base64,"+btoa(binary));
        },
        error: function(xhr, status, errorThrown){
          alert("Error in getting document "+status);
        }
      });
    }
  });
});


function myFunction(imgs) {
  // Get the expanded image
  var expandImg = document.getElementById("selectedImg");
  // Use the same src in the expanded image as the image being clicked on from the grid
  expandImg.src = imgs.src;
  expandImg.alt = imgs.alt;
  // Show the container element (hidden with CSS)
  expandImg.parentElement.style.display = "block";
}
