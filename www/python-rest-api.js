$(function () {

  var API_URL=window.location.protocol + '//' + window.location.hostname + ":5000"

  if (ENV_API_URL !== '') {
    API_URL=ENV_API_URL;
  }

  function get_ids() {
    $.ajax({
      url: API_URL+"/id",
      type: 'GET',
      success: function (response) {
        ids="api: " + response['api_host'] + " db: " + response['db_host'];
        $('#ids').append(document.createTextNode(ids));
      }
    });
  }

  function del_entry(key){
    $.ajax({
      url: API_URL+"/data/del/"+key,
      type: 'DELETE',
      success: function (response) {
        reload_table()
      }
    });
  }

  function reload_table() {
    $.ajax({
      url: API_URL+"/data",
      type: 'GET',
      success: function (response) {
        $('#data_table tr').remove();
        $('#data_table').append('<tr><td"><center>k</center></td><td><center>v</center></td><td><center>del</center></td><tr>');
        for(i=0;i<response.length;i++){
          $('#data_table').append('<tr><td>' +  response[i][0] + '</td><td>' + response[i][1] + '</td><td><button type="button" id="del_btn" class="btn btn-secondary btn-sm" data-key="'+response[i][0]+'">del</button></td></tr>');
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
      url: API_URL+"/data/add",
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
  $(document).on('click', '#del_btn', function(){
    del_entry($(this).data("key"))
  });

  $(document).ready( function(){
    console.log("API_URL: " + API_URL);
    reload_table(); 
    get_ids();
  } );
});
