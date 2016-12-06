/**
 * Created by Himel on 12/1/2016.
 */
$('#application_corporate_name').addClass('form-control');
$('#application_pps').addClass('form-control');
function _on_gname_change(evt){
    if ($('#application_application_size').val()=='Corporate') {
        $('#application_corporate_name__row').fadeIn();
        $('#application_largest_practice__row').fadeIn();
    } else {
        $('#application_corporate_name__row').fadeOut();
        $('#application_largest_practice__row').fadeOut();
    }
}
$('#application_application_size').change(_on_gname_change);
_on_gname_change();