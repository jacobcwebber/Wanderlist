// Options used for search
var options = {
    shouldSort: true,
    threshold: 0.075,
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
        'DestName',
        'CountryName',
        'Tags',
        'ContName'
    ]
};

var fuse = new Fuse(dests, options);
var allDestIds = [];

// Only shows first 20 destinations on page load
$('.dest').slice(0, 20).removeClass('hidden');

// Adds the IDs of all destinations to an array
$('.dest').each(function() {
    allDestIds.push(this.id)
});

// Triggers search on button click
$('.search-btn').click(function(event) {
    searchDests()
});

// Triggers search on enter key press when in input box
$('.search').keypress(function(e) {
    if(e.which == 13) {
        searchDests();
    }
});

function searchDests() {
    // Create/truncate list of IDs of destinations matching previous search
    var resultIds = [];

    // Grab search query from input field and plug into fuse.js to get JSON results
    var query = $('.tag:first-of-type').text();
    var results = fuse.search(query);

    // If there are not results, then hide all destinations and show "No results" text
    if (Object.keys(results).length == 0 && query != '') {
        $('.no-results').removeClass('hidden');
        $('.dest').each(function() {
            $(this).addClass('hidden');
        });
    
    // If there are results
    } else {
        // Hide the "No results" text
        $('.no-results').addClass('hidden');

        // Create array of IDs of dests in result
        for (var i = 0; i < results.length; i++) {
            resultIds.push("dest".concat(results[i].DestID));
        };

        // Compare resultIds array to array of all destIds, unhide all destinations, then hide those that
        // do not appear in resultsIds list
        for (var i = 0; i < allDestIds.length; i++) {
            $(`.dest#${allDestIds[i]}`).removeClass('hidden');
            if (resultIds.indexOf(allDestIds[i]) == -1 && query != '') {
                $(`.dest#${allDestIds[i]}`).addClass('hidden');
            };
        };
    };  
};

$('#search').tagsinput({
    confirmKeys: [9, 13, 44],
    trimValue: true,
    typeahead: {
        afterSelect: function(val) {this.$element.val(""); },
        limit: 5,
        source: searchList
    },
    freeInput: true    
});

$('.bootstrap-tagsinput input').on('keypress', function(e){
    if (e.keyCode == 13){
      e.keyCode = 188;
      e.preventDefault();
    };
  });