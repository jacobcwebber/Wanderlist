//Initializing variables
let featBox = $('.box:first-of-type');
let featDestWrapper = $('.feat-dest-wrapper');
let featDestImg = $('#feat-dest-img');
let featDestName = $('#feat-dest-name');
let featCountryName = $('#feat-country-name');
let featDestDesc = $('#feat-dest-desc');
let featDestTags = $('#feat-dest-tags');

let resultsBox = $('box:last-of-type');

$('#location').typeahead({
  hint: false,
  highlight: true,
  minLength: 1,
  source: locations
});

$('#keywords').typeahead({
  hint: false,
  highlight: true,
  minLength: 1,
  source: tags
})

// Show or hide Placeholder depending on existence of tags
$('#keywords').on('itemAdded', () => {
  $('.search-input input').attr('placeholder', '');
});

$('#keywords').on('itemRemoved', () => {
  if ($('.label').length == 0) {
    $('.search-input input').attr('placeholder', 'Filter by keywords');
  }
});

$('.item-mid').click(e => {
  let id = e.target.id;
  $.ajax({
    type: 'POST',
    url: '/alter-featured-dest',
    data: {
      id: id
    }
  })
    .done(response => {
      featDestImg.attr('src', response[0][0].img_url);
      featDestName.text(response[0][0].dest_name);
      featCountryName.text(response[0][0].country_name);
      featDestDesc.html(response[0][0].description);
      featDestTags.empty();
      let tags = response[1];
      $.each(tags, i => {
        featDestTags.append(
          `<a href='/search?keywords=${tags[i]}' class='label label-lg'>${tags[i]}</a> `
        );
      });
      featBox.removeClass('hide');
      $.smoothScroll({
        offset: -64,
        scrollTarget: featBox
      });
    })
    .fail(error => {
      console.log(error);
    });
});

$('.fa-times-circle').click(e => featBox.addClass('hide'));

$(window).on('load', function() {
  $('.loading').addClass('hide');
  $('.five-wide').removeClass('hide');
});
