var radius = 400 / 2;
// var radius = 600 / 2;

var tree = d3.layout.tree()
    // .size([360, radius - 120]);
    // .size([360, radius - 80]);
    .size([360, radius]);
    // The below was making it break for trees of one parent and one child
    // .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var line = d3.svg.line()
  .interpolate("basis")
  .x(function(d) {
    var r = d.y, a = (d.x - 90) / 180 * Math.PI;
    return r * Math.cos(a);
  })
  .y(function(d) {
    var r = d.y, a = (d.x - 90) / 180 * Math.PI;
    return r * Math.sin(a);
  });
  // .interpolate("basis");
  // .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var vis = d3.select("#chart").append("svg")
    .attr("width", radius * 2 + 10)
    .attr("height", radius * 2 + 10)
  .append("g")
    .attr("transform", "translate(" + (radius+10) + "," + radius + ")");

function get_rotation(d) {
  if (d.x > 270) {
    return 180 + d.x;
  }
  else if (d.x > 180) {
    return d.x;
  }
  else if (d.x <= 180) {
    return 90 - d.x;
  }
}

function get_tine_url(fcn, story_id, tine_id) {
  return '/story_fork/' + fcn + '/' + story_id + '/' + tine_id;
}

function highlight_tweet_node(obj) {
    $.each($('.node').children('circle'), function() {
      if ($(this).attr('class') == 'root-circle'){
        $(this).css('fill', 'black');
      }
      else {
        $(this).css('fill', 'white');
      }
    });
    var tine_circle = $(obj).children("circle");
    tine_circle.css('fill', 'orange');

    var tine = $(obj).children("text");  
    var story_id = tine.attr("story_id");
    var tine_id = tine.attr("tine_id");

    var url = get_tine_url('tine_embedded', story_id, tine_id);
    var tine_url =  tine.attr("url");
    $('#tweet_link').html('Loading tweet...').load(url);
    // $('#tweet_update_link').html(' and <a href="/story_fork/update/pleasedoit">update</a>');
    $('#tweet_link').css('outline', 'orange solid');

    var url = get_tine_url('tine_path', story_id, tine_id);
    $('#tweet_story').html('Loading story...').load(url);
    var url = get_tine_url('reply', story_id, tine_id);
    $('#tweet_reply').html('Reply!').load(url);
}

function load_data(json) {
  var nodes = tree.nodes(json);

  var link = vis.selectAll("path.link")
      .data(tree.links(nodes))
    .enter().append("path")
      .attr("class", "link")
      // .attr("extra-source", function(d) {return Object.keys(d.source);})
      // .attr("extra-target", function(d) {return Object.keys(d.target);})
      .attr("extra-source-x", function(d) {return d.source.x;})
      .attr("extra-source-y", function(d) {return d.source.y;})
      .attr("extra-target-x", function(d) {return d.target.x;})
      .attr("extra-target-y", function(d) {return d.target.y;})
      // .attr("extra", line);
      .attr("d", diagonal);

/*
SVG HELP: http://www.ibm.com/developerworks/library/x-svgint/

TO DO:
  * make graph lines straight
    https://github.com/mbostock/d3/wiki/SVG-Shapes
    http://jsfiddle.net/qsEbd/30/
  * highlight path to node

DONE:
  * give url path to highlight story as well, for linking from tweet
  * clicking node should show story leading up to that tine
    javascript so it's not a new url
    link to tweet visible only there
  * why is shape not centered in div?
    has to do with spacing made for text labels...
    currently, having text face to center so i can get rid of outer-circle spacing
  * hovering should only show text of that node
    make a div for each tine; add the hover jquery to each
*/

  var node = vis.selectAll("g.node")
      .data(nodes)
    .enter().append("g")
      .attr("class", "node")
      .attr("desc", function(d) { return d.name; })
      .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })

  node.append("circle")
      .attr("class", function(d) { return d.index==1 ? "root-circle" : "nonroot-circle"; })
      .attr("r", 5);

  node.append("text")
      .attr("dy", ".31em")

      // turn in/out
      // .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
      // .attr("transform", function(d) { return d.x < 180 ? "rotate(" + get_rotation(d) + ")translate(8)" : "rotate(" + get_rotation(d) + ")translate(-8)"; })
      .attr("text-anchor", function(d) { return d.x < 180 ? "end" : "start"; })
      .attr("transform", function(d) { return d.x < 180 ? "rotate(" + get_rotation(d) + ")translate(-8)" : "rotate(" + get_rotation(d) + ")translate(8)"; })

      .attr("url", function(d) { return d.url; })
      .attr("story_id", function(d) {return d.story_index;})
      .attr("tine_id", function(d) {return d.index;})
      .attr("id", "tine_text")
      .attr("class", function(d) { return "tine-" + d.index; })
      .text(function(d) { return d.name; });

  $('.root-circle').css('fill', 'black');
  $('.node').children('text').hide();
  var tine_index = $('#tine_index').attr('value');
  if (tine_index >= 0) {
    highlight_tweet_node($('.tine-' + tine_index).parent());
  }

  $('body').on('mouseover', '.node', function () {
    var tine = $(this).children("text");
    var tine_class =  tine.attr("class");
    $('.' + tine_class).show();
  });
  $('body').on('mouseout', '.node', function () {
    var tine_class =  $(this).children("text").attr("class");
    $('.' + tine_class).hide();
  });
  $('body').on('click', '.node', function () { highlight_tweet_node($(this)) });

};
