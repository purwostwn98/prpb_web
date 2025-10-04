(function($) {
    $(document).ready(function() {
      // select spbu field
      var spbuField = $('#id_spbu');
      // make on change event
      spbuField.change(function() {
        // auto fill id_estimated_distance_km field based on spbu value
        // Get the selected option from the SPBU dropdown
        $('#id_estimated_distance_km').val(12);
        // alert('SPBU field changed to: ' + $(this).val());
      });
    });
})(typeof django !== 'undefined' && django.jQuery ? django.jQuery : jQuery);

// admin/shippingto_autofill.js