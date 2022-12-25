$(function () {

  function reload_table() {
    $.ajax({
      url: "http://192.168.1.6:5000/data",
      type: 'GET',
      success: function (response) {
        $('#data_table tr').remove()
        $('#data_table').append('<tr><td>k</td><td>v</td><tr>')
        for(i=0;i<response.length;i++){
          $('#data_table').append( '<tr><td>' +  response[i][0] + '</td><td>' + response[i][1] + '</td></tr>');
        }
      }
    });
  }

  function send_post(){
    var data = {};
    data[$('#key_form').val()] = $('#value_form').val()
    body = JSON.stringify(data)
    console.log(body)
    $.ajax({
      url: "http://192.168.1.6:5000/data/add",
      contentType: "application/json",
      data: body,
      dataType: "json",
      type: 'POST',
      success: function (response) {
        reload_table()
      }
    });
  }

  $('#refresh_btn').click( function(){reload_table()} );
  $('#add_btn').click( function(){send_post()} );

  $(document).ready( function(){reload_table()} );
});
