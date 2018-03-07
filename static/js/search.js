//Basic search
// var basicSearchOptions = {
//     shouldSort: true,
//     threshold: 0.25,
//     location: 0,
//     distance: 100,
//     maxPatternLength: 32,
//     minMatchCharLength: 1,
//     keys: [
//         'DestName',
//     ]
// };


// $('#basic-search-btn').click(function() {
//     basicSearch();
// });

// function basicSearch() {
//     basicSearchQuery = $('#basic-search').val();
//     basicSearchFuse = new Fuse(dests, basicSearchOptions);
//     basicSearchResults = basicSearchFuse.search(basicSearchQuery);
//     console.log(basicSearchResults);
// };


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

var allDestIds = [];

// Adds the IDs of all destinations to an array
$('.item').each(function() {
    allDestIds.push(this.id)
});

// Triggers search on button click
$('#adv-search-btn').click(function(event) {
    advSearch()
});

// Triggers search on enter key press when in input box
$('#adv-search').keypress(function(e) {
    if(e.which == 13) {
        advSearch();
    }
});

function advSearch() {
    advSearchQuery = $('#adv-search').val(); 
    $('.item-group').toggleClass('hidden');
    $('#loading').toggleClass('hidden');

    $.getJSON({
        dataType: "json",
        url: "/getSearchResults",
        data: {
            q: advSearchQuery
        }
    }).done(function(response) {
        console.log(response);
        $('#loading').toggleClass('hidden');

    });

    // Create list of IDs of destinations matching previous search
//     var resultIds = [];
//     var query = '';
//     var fuse = new Fuse(dests, options);

//     $('.tag').each(function() {
//         query = $(this).text();
//         destOptions = fuse.search(query);
//         fuse = new Fuse(destOptions, options);
//     });

//     var results = destOptions;
    
//     // If there are not results, then hide all destinations and show "No results" text
//     if (Object.keys(results).length == 0 && query != '') {
//         $('.no-results').removeClass('hidden');
//         $('.item').each(function() {
//             $(this).addClass('hidden');
//         });
    
//     // If there are results
//     } else {
//         // Hide the "No results" text
//         $('.no-results').addClass('hidden');

//         // Create array of IDs of dests in result
//         for (var i = 0; i < results.length; i++) {
//             resultIds.push("dest".concat(results[i].DestID));
//         };

//         // Compare resultIds array to array of all destIds, unhide all destinations, then hide those that
//         // do not appear in resultsIds list
//         for (var i = 0; i < allDestIds.length; i++) {
//             $(`.item#${allDestIds[i]}`).removeClass('hidden');
//             if (resultIds.indexOf(allDestIds[i]) == -1 && query != '') {
//                 $(`.item#${allDestIds[i]}`).addClass('hidden');
//             };
//         };
//     };  
};

$('#adv-search').tagsinput({
    confirmKeys: [9, 13, 44],
    trimValue: true,
    typeahead: {
        afterSelect: function() {this.$element.val(''); },
        source: searchList
    },
    freeInput: true    
});



// Get rid of placeholder if there is at least one tag
// $('.bootstrap-tagsinput input').keypress(function() {
//     var numberOfTags = $('.tag').length
//     if (numberOfTags != 0) {
//         $(this).attr('placeholder', '')   
//     } else {
//         $(this).attr('placeholder', 'Search...')
//     }
// });
