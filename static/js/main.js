$(document).ready(function() {

	// Pop-up for adding entries
	$('a#active' || '#black').click(function() {
		$('form.add-entry').toggle();
		$('#black').toggle();
	});

	$('#black').click(function() {
		$('form.add-entry').hide();
		$('#black').hide();
	});

	// Hide unnecessary select options
	$('select.select-type').hide();
	$('#family').change(function() {
		$('select.select-type').hide();
		$('#' + $(this).val()).show();
	});

});