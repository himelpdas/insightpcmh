/**
 * Created by Himel on 12/1/2016.
 */
$('#application_authorized_representative').addClass('form-control');
$('#application_pps').addClass('form-control');
function _on_gname_change(evt){
    if ($('#application_application_size').val()=='Corporate') {
        $('#application_authorized_representative__row').fadeIn();
        $('#application_largest_practice__row').fadeIn();
    } else {
        $('#application_authorized_representative__row').fadeOut();
        $('#application_largest_practice__row').fadeOut();
    }
}
$('#application_application_size').change(_on_gname_change);
_on_gname_change();