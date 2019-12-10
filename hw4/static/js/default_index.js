// This is the js for the default/index.html view.
var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};

    // TODO: Search
    /*  self.do_search = function () {
        $.getJSON(search_url,
            {search_string: self.vue.search_string,
            product_list: self.vue.product_list},
            function (data) {
                self.vue.strings = data.strings;
            });
    }; */

    // Adds a review:
    self.add_review = function (product_idx) {
        // We disable the button, to prevent double submission.
        $.web2py.disableElement($("#add-review"));
        var sent_review = self.vue.form_review; // Makes a copy 
        var p = self.vue.product_list[product_idx];
        // TODO: Set confirmcheck to true.
        self.vue.confirmcheck = true;
        setInterval(
            function() {self.vue.confirmcheck = false},
            2000
        )
        $.post(add_review_url,
            // Data we are sending.
            {
                review: self.vue.form_review,
                product_id: product_idx
            },
            // What do we do when the review succeeds?  
            function (data) {
                // Re-enable the button.
                $.web2py.enableElement($("#add-review"));
                // Clears the form.
                self.vue.form_review = "";
                // Adds the review to the list of reviews. 
                var new_review = {
                    id: data.review_id,
                    review: sent_review,
                };
                self.vue.review_list.unshift(new_review);
                // We re-enumerate the array.
                self.process_reviews();
            });
        // If you put code here, it is run BEFORE the call comes back.
    };

    // Grab a list of products.
    self.get_products = function() {
        $.getJSON(get_product_list_url,
            function(data) {
                // I am assuming here that the server gives me a nice list
                // of products, all ready for display.
                self.vue.product_list = data.product_list;
                // Post-processing.
                self.process_products();
            }
        );
    };

    // Grab a list of reviews.
    self.get_reviews = function() {
        $.getJSON(get_review_list_url,
            function(data) {
                self.vue.review_list = data.review_list;
            }
        );
    };

    self.process_products = function() {
        // This function is used to post-process products, after the list has been modified
        // or after we have gotten new products. 
        // We add the _idx attribute to the products. 
        enumerate(self.vue.product_list);
        self.vue.product_list.map(function (e) {
            // I need to use Vue.set here, because I am adding a new watched attribute
            // to an object.  See https://vuejs.org/v2/guide/list.html#Object-Change-Detection-Caveats
            
            // Number of stars to display.
            Vue.set(e, '_num_stars_display', e.rating);
            Vue.set(e, '_num_stars_display_review', e.rating);
            // Reviews to display.
            Vue.set(e, '_reviews', []);
            // Are the reviewers known?
            Vue.set(e, '_reviews_known', false);
            // We can show the reviews finally.
            Vue.set(e, '_show_reviews', false);
        });
    };

    self.process_reviews = function() {
        // This function is used to post-process products, after the list has been modified
        // or after we have gotten new products. 
        // We add the _idx attribute to the products. 
        enumerate(self.vue.review_list);
        // We initialize the smile status to match the like. 
        self.vue.review_list.map(function (e) {
            // I need to use Vue.set here, because I am adding a new watched attribute
            // to an object.  See https://vuejs.org/v2/guide/list.html#Object-Change-Detection-Caveats
        });
    };

    // Code for getting and displaying the list of reviews. 
    self.show_reviews = function(product_idx) {
        var p = self.vue.product_list[product_idx];
        p._show_reviews = !p._show_reviews;
        // If user has clicked show reviews:
        if (p._show_reviews) {
            $.getJSON(get_reviews_url, {product_id: p.id}, function (data) {
                p._reviews = data.reviews
                p._reviews_known = true;
            })
        } else { // else, close all other reviews.
            for (i = 0; i < self.vue.product_list.length; i++) {
                var p = self.vue.product_list[i];
                p._show_reviews = false;
                p._reviews_known = false;
            }
        }
    };

    // Code for star ratings.
    self.stars_out = function (product_idx) {
        // Out of the star rating; set number of visible back to rating.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display = p.rating;
    };

    self.stars_over = function(product_idx, star_idx) {
        // Hovering over a star; we show that as the number of active stars.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display = star_idx;
    };

    self.stars_out_review = function (product_idx) {
        // Out of the star rating; set number of visible back to rating.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display_review = p.rating;
    };

    self.stars_over_review = function(product_idx, star_idx) {
        // Hovering over a star; we show that as the number of active stars.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display_review = star_idx;
    };

    self.set_stars = function(product_idx, star_idx) {
        // The user has set this as the number of stars for the product.
        var p = self.vue.product_list[product_idx];
        p.rating = star_idx;
        // Sends the rating to the server.
        $.post(set_stars_url, {
            product_id: p.id,
            rating: star_idx
        });
    };

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            confirmcheck: false,
            form_review: "",
            product_list: [],
            review_list: [],
            strings: [],
            search_string: '',
            star_indices: [1, 2, 3, 4, 5],
        },
        methods: {
            // Star ratings.
            stars_out: self.stars_out,
            stars_over: self.stars_over,
            stars_out_review: self.stars_out_review,
            stars_over_review: self.stars_over_review,
            set_stars: self.set_stars,
            // Reviews
            show_reviews: self.show_reviews,
            hide_reviews: self.hide_reviews,
            get_reviews: self.get_reviews,
            add_review: self.add_review,
            // Search (TODO)
            // do_search: self.do_search
        }

    });

    // If we are logged in, shows the form to add products.
    if (is_logged_in) {
        $("#add_review").show();
    }

    // Gets the products.
    self.get_products();
    self.get_reviews();
    // TODO: self.do_search();

    return self;
};

var APP = null;

// No, this would evaluate it too soon.
// var APP = app();

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
