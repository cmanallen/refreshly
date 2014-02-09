$(document).ready(function() {
	
	// Pop-up for adding entries
	$('a#active').click(function() {
		$('form.add-entry').toggle();
	});

	// Hide unnecessary select options.
	$('#family').change(function() {
		$('select.select-type').hide();
		$('#' + $(this).val()).show();
	});

});