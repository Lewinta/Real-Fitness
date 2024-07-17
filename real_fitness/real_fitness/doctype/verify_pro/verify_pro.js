// Copyright (c) 2024, Rainier J Polanco and contributors
// For license information, please see license.txt


{

	function renew(frm){
		ammend_doc(frm);
	}
	
	function re_generate(frm){
		ammend_doc(frm);
	}

	function ammend_doc(frm) {
		const { doc } = frm;

		if (
			doc.status === "Draft"
		) {
			return ; // add only if the document is not in draft
		}


		frm.copy_doc(function(d) {			
			d.amended_from = doc.name;
			d.authorization_code = '';
		}, doc.name);

		// button.removeClass("btn-default");
		// button.addClass("btn-primary");
	}



	frappe.ui.form.on('Verify Pro', {
		renew,re_generate
	});
	
}
