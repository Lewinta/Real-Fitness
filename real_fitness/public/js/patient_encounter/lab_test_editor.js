frappe.provide("fitness");

fitness.LabTestEditor = class {
    constructor(wrapper, frm, disable) {
        this.wrapper = wrapper;
        this.frm = frm;
        this.disable = disable;
        this.multicheck = frappe.ui.form.make_control({
            parent: wrapper,
            df: {
                fieldname: "lab_tests",
                fieldtype: "MultiCheck",
                select_all: true,
                columns: "15rem",
                get_data: () => {
                    const { lab_test_prescription } = frm.doc;
                    const selected_lab_tests = lab_test_prescription.map(
                        d => d.lab_test_code
                    );
                    return frappe
                        .xcall("real_fitness.controllers.patient_encounter.patient_encounter.get_all_lab_tests")
                        .then((lab_tests) => {
                            return lab_tests.map((lab_test) => {
                                return {
                                    label: __(lab_test),
                                    value: lab_test,
                                    checked: selected_lab_tests.includes(lab_test),
                                };
                            });
                        });
                },
                on_change: () => {
                    this.set_lab_tests_in_table();
                    this.frm.dirty();
                },
            },
            render_input: true,
        });
    }
    set_enable_disable() {
        $(this.wrapper)
            .find('input[type="checkbox"]')
            .attr("disabled", this.disable ? true : false);
    }
    show() {
        this.reset();
        this.set_enable_disable();
    }
    set_lab_tests_in_table() {
        const lab_test = this.multicheck.get_value();
        this.frm.doc.lab_test_prescription = [];
        lab_test.forEach((lab_test_code) => {
            const d = this.frm.add_child("lab_test_prescription");
            d.lab_test_code = lab_test_code;
        });
    }

}