// Copyright (c) 2023, Miguel Higuera and contributors
// For license information, please see license.txt

{frappe.ui.form.on("Patient", {
    refresh(frm) {
        frm.trigger("set_intro_for_viral_condition");
        frm.trigger("setup_carousel");
    },
    referral_type(frm) {
        const { doc } = frm;

        if (doc.referral_type == "Other") {
            frm.set_value("referrer", null);
        }

        if (doc.referral_type == "Customer" || doc.referral_type == "Healthcare Practitioner") {
            frm.set_value("other_referrer", null);
        }

        if (doc.referral_type == "") {
            frm.set_value("referrer", null);
            frm.set_value("other_referrer", null);
        }
    },
    setup_carousel(frm){
        const { attachments } = frm;

        const attachment_list = attachments.get_attachments();
        if (
            attachment_list.length > 0
        ) {
            jQuery("#view-todo-attachment-btn").remove();
            jQuery(
                `
                <li id="view-todo-attachment-btn">
                    <br>
                    <button class="data-pill btn">
                        <span class="pill-label ellipsis"> ${__("View in Slider")} </span>
                        <svg class="icon icon-sm">
                            <use href="#icon-right"></use>
                        </svg>
                    </button>
                </li>
                `
            )
            .appendTo(`ul.sidebar-menu.form-attachments`)
            .find("button")
            .click(() => {
                frm.current_carousel = new Carousel(
                    frm, attachment_list.filter(function(d) {
                        // only images... all known types
                        return ["Image", "JPEG", "JPG", "PNG", "GIF", "SVG"].includes(d.file_url.split('.').pop().toUpperCase());
                    })
                );
            });
        }
    },

    set_intro_for_viral_condition(frm) {
        const { doc } = frm;

        if (doc.viral_condition) {
            frm.set_intro(
                `<i class='fa fa-exclamation-triangle' style='color:red'></i> Paciente con virus de <b>${frm.doc.viral_condition}</b>`,
                'red'
            );
        }
    },
    


});

class Carousel {
    constructor(frm, attachments){
        this.frm = frm;
        this.attachments = attachments;
        this.current_index = 0;
        this.render();
    }

    render() {
        const wrapper = this.get_wrapper();

        // <div class="carousel-item active">
        //     <img class="d-block w-100" src="..." alt="First slide">
        // </div>
        // <div class="carousel-item">
        //     <img class="d-block w-100" src="..." alt="Second slide">
        // </div>
        // <div class="carousel-item">
        //     <img class="d-block w-100" src="..." alt="Third slide">
        // </div>

        const slider = jQuery(`
            <div
                id="todo-slider"
                class="carousel slide"
                data-ride="carousel"
            ></div>
        `).appendTo(wrapper);

        const indicators_wrapper = jQuery(`
            <ol class="carousel-indicators"></ol>
        `).appendTo(slider);

        const inner_wrapper = jQuery(`
            <div class="carousel-inner"></div>
        `).appendTo(slider);

        this.attachments.map((attachment, index) => {
            const active = index === 0 ? "active" : "";

            jQuery(`
                <li
                    data-target="#todo-slider"
                    data-slide-to="${index}"
                    class="${active}"
                >
                </li>
            `).appendTo(indicators_wrapper);
            return jQuery(`
                <div class="carousel-item ${active}">
                    <img
                        class="d-block w-100"
                        src="${attachment.file_url}"
                        alt="${attachment.file_name}"
                    />

                    <div style="background-color: rgba(2, 2, 2, .6)" class="carousel-caption d-none d-md-block">
                        <h3>${attachment.file_name}</h3>
                    </div>
                </div>
            `).appendTo(inner_wrapper);
        });
        
        jQuery(`
            <a class="carousel-control-prev" href="#todo-slider" role="button" data-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="sr-only">Previous</span>
            </a>
        `).click(event => {
            event.preventDefault();
            event.stopPropagation();

            slider.carousel("prev");
        }).appendTo(slider);

        jQuery(`
            <a class="carousel-control-next" href="#todo-slider" role="button" data-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="sr-only">Next</span>
            </a>
        `).click(event => {
            event.preventDefault();
            event.stopPropagation();

            slider.carousel("next");

            //
        }).appendTo(slider);

        this.slider = slider;
    }

    get_wrapper(){
        const fields = [
            {
                fieldname: "wrapper",
                fieldtype: "HTML",
                label: __("Attachments"),
            },
        ];

        const title = __("Attachments Slider");
        const dialog = new frappe.ui.Dialog({
            title, fields, size: "extra-large"
        });

        dialog.show();

        console.log({ dialog });

        this.dialog = dialog;
        return dialog.get_field("wrapper").$wrapper;
    }
}



}