function show_image(e, width=400) {
  var obj = $(e);
  var div = obj.parent();
  if (obj.find('img').length)
    obj.find('img').show();
  else {
    var img = $('<img width="' + width + '">');
    var url = div.find('input').first().val();
    img.attr('src', url);
    img.attr('title', 'Click to close.');
    img.on('click', function(e){hide_image(e);});
    img.appendTo(div);
    obj.hide();
  }
}

function show_image_td(e, width=400) {
  var obj = $(e);
  var div = obj.parent();
  if (obj.find('img').length)
    obj.find('img').show();
  else {
    var img = $('<img width="' + width + '">');
    var url = div.find('input').first().val();
    var td = div.closest('td');
    img.attr('src', url);
    img.attr('title', 'Click to close.');
    img.on('click', function(e){hide_image(e);});
    img.appendTo(td);
    obj.hide();
  }
}

function hide_image(e) {
  var img = $($(e.target)[0]);
  img.hide();
  var div = img.parent();
  div.find('a').show();
}