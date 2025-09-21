/** @odoo-module **/


    /** @odoo-module **/
//
//    import { FormController } from "@web/views/form/form_controller";
//    import { patch } from "@web/core/utils/patch";
//    import { _t } from "@web/core/l10n/translation";
//    import { useService } from "@web/core/utils/hooks";
//
//    console.log("➡️ JS Loaded: Odoo 17 Patch Demo");
//
//
//    patch(FormController.prototype, 'onsave_notification', {
//        setup() {
//            this._super(...arguments);
//            this.notification = useService("notification");
//        },
//        async saveButtonClicked() {
//            var self = this;
//            return this._super(...arguments).then(function () {
//                self.notification.add(_t("Record saved successfully!"), {
//                    title: _t("Success"),
//                    type: "success",
//                    // You can add more options like:
//                    // sticky: true, // Makes the notification stay until manually closed
//                    // timeout: 5000, // Disappears after 5 seconds
//                });
//            });
//        }
//    });


import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";


this code will work until 1st console.log

console.log("➡️ JS Loaded: Odoo 17 Patch Demo");

patch(FormController.prototype, {
    async saveRecord() {
        console.log("🔍 saveRecord method called (OWL patch)");
        // Call original behavior
        return await this._super(...arguments);
    },
});



///** @odoo-module **/
//
//import { CounterComponent } from "./counter_component";
//import { mount } from "@odoo/owl";
//
//console.log("➡️ JS Loaded: Mount script started");
//
//document.addEventListener("DOMContentLoaded", async () => {
//    console.log("✅ DOM fully loaded");
//
//    const root = document.getElementById("counter-root");
//    console.log("🔍 Looking for element #counter-root:", root);
//
//    if (root) {
//        console.log("📦 Mounting CounterComponent...");
//        await mount(CounterComponent, { target: root });
//        console.log("✅ CounterComponent successfully mounted.");
//    } else {
//        console.warn("❌ Mount point #counter-root not found.");
//    }
//});
